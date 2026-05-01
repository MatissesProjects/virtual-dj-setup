using System;
using System.IO;
using System.Threading;
using NAudio.Wave;

namespace VirtualDj.Engine
{
    public class HeadlessHost
    {
        private readonly string _filePath;

        public HeadlessHost(string filePath)
        {
            _filePath = filePath;
        }

        public void Run()
        {
            if (!File.Exists(_filePath))
            {
                Console.WriteLine($"[HEADLESS] Error: File not found - {_filePath}");
                return;
            }

            Console.WriteLine($"[HEADLESS] Starting Simulation Gym for: {_filePath}");

            using var reader = new AudioFileReader(_filePath);
            using var sharedMemoryService = new SharedMemoryService();
            using var deck = new VirtualDeck("HeadlessDeck", reader.WaveFormat);
            var intentExecutor = new IntentExecutor(deck.Pipeline);

            // Need an intent listener or we can just read commands from MMF in the future
            using var intentListener = new IntentListener();
            intentListener.IntentReceived += (intent) =>
            {
                intentExecutor.Execute(intent);
            };
            intentListener.Start();

            deck.Pipeline.FeaturesCalculated += (s, frame) =>
            {
                sharedMemoryService.WriteFeatureFrame(frame, 0, frame.MagnitudeSpectrum ?? Array.Empty<float>());
                
                var (freq, gain) = sharedMemoryService.ReadDuckingParams();
                if (freq > 0)
                {
                    deck.Pipeline.SetDucking(freq, gain);
                }
            };

            // Set initial state
            sharedMemoryService.WriteIsDone(false);
            sharedMemoryService.ClearStepCommand();

            float[] floatBuffer = new float[8192];
            bool isEof = false;

            Console.WriteLine("[HEADLESS] Waiting for Python Gym to step the environment...");

            while (!isEof)
            {
                var (command, stepSize) = sharedMemoryService.ReadStepCommand();

                if (command == 1 && stepSize > 0)
                {
                    // Python requested a step
                    int samplesToRead = stepSize * reader.WaveFormat.Channels;
                    if (samplesToRead > floatBuffer.Length)
                    {
                        floatBuffer = new float[samplesToRead];
                    }

                    int samplesRead = reader.Read(floatBuffer, 0, samplesToRead);

                    if (samplesRead > 0)
                    {
                        deck.Process(floatBuffer, samplesRead, reader.WaveFormat);
                        // Acknowledge step completed
                        sharedMemoryService.ClearStepCommand();
                    }
                    
                    if (samplesRead < samplesToRead)
                    {
                        // EOF reached
                        isEof = true;
                        sharedMemoryService.WriteIsDone(true);
                        sharedMemoryService.ClearStepCommand();
                        Console.WriteLine("[HEADLESS] End of file reached. Episode Done.");
                    }
                }
                else
                {
                    // Yield briefly to avoid 100% CPU lock while waiting for Python
                    Thread.Sleep(1);
                }
            }

            intentListener.Stop();
            Console.WriteLine("[HEADLESS] Simulation complete.");
        }
    }
}
