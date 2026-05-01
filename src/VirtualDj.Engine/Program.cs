using System;
using NAudio.Wave;

namespace VirtualDj.Engine
{
    class Program
    {
        static void Main(string[] args)
        {
            if (args.Length >= 2 && args[0] == "--headless")
            {
                var host = new HeadlessHost(args[1]);
                host.Run();
                return;
            }

            Console.WriteLine("Virtual DJ Engine starting (Live Mode)...");

            using var captureService = new WasapiCaptureService();
            using var sharedMemoryService = new SharedMemoryService();
            using var intentListener = new IntentListener();
            
            // Track 13: Multi-Deck & Crossfader
            using var deckA = new VirtualDeck("Deck A", captureService.WaveFormat);
            using var deckB = new VirtualDeck("Deck B", captureService.WaveFormat);
            using var masterMixer = new MasterMixer(deckA, deckB, captureService.WaveFormat);
            
            var intentExecutor = new IntentExecutor(deckA.Pipeline);
            using var midiService = new MidiService(deckA.Pipeline);
            var playlistManager = new PlaylistManager();

            // Mock Playlist
            playlistManager.AddSong("Get Lucky", "Daft Punk");
            playlistManager.AddSong("Blinding Lights", "The Weeknd");
            playlistManager.AddSong("Levitating", "Dua Lipa");
            
            float[] floatBuffer = new float[8192];

            intentListener.IntentReceived += (intent) =>
            {
                intentExecutor.Execute(intent);
            };

            deckA.Pipeline.FeaturesCalculated += (s, frame) =>
            {
                // 1. Write to Shared Memory for Python (passing current song index and full FFT)
                sharedMemoryService.WriteFeatureFrame(frame, 0, frame.MagnitudeSpectrum ?? Array.Empty<float>());
                sharedMemoryService.WriteCrossfaderPosition(masterMixer.Crossfader.Position);

                // 2. Read Ducking Commands from Python (Bi-directional MMF)
                var (freq, gain) = sharedMemoryService.ReadDuckingParams();
                if (freq > 0)
                {
                    deckA.Pipeline.SetDucking(freq, gain);
                }

                // 3. Read Crossfader from Python (AI/UI control)
                masterMixer.Crossfader.Position = sharedMemoryService.ReadCrossfaderPosition();

                // 4. Local Debug Output
                double decibels = 20 * Math.Log10(frame.Rms);
                if (double.IsInfinity(decibels)) decibels = -100;
                var song = playlistManager.CurrentSong;
                Console.Write($"\r[{song?.Title}] RMS: {decibels:F1} dB | X-Fader: {masterMixer.Crossfader.Position:F2} | Auth: {frame.Authority}    ");
            };

            captureService.DataAvailable += (s, e) =>
            {
                var waveBuffer = new WaveBuffer(e.Buffer);
                int sampleCount = e.BytesRecorded / 4;
                
                if (sampleCount > floatBuffer.Length)
                    floatBuffer = new float[sampleCount];

                for(int i = 0; i < sampleCount; i++)
                {
                    floatBuffer[i] = waveBuffer.FloatBuffer[i];
                }

                // Process through Decks (Currently both getting same input for demo)
                deckA.Process(floatBuffer, sampleCount, captureService.WaveFormat);
                deckB.Process(floatBuffer, sampleCount, captureService.WaveFormat);
            };

            intentListener.Start();
            midiService.Start();
            masterMixer.Start();
            captureService.Start();

            Console.WriteLine("Press any key to stop... (Press 'M' for Manual, 'C' to toggle Crossfader)");
            
            while (true)
            {
                if (Console.KeyAvailable)
                {
                    var key = Console.ReadKey(true).Key;
                    if (key == ConsoleKey.M)
                    {
                        deckA.Pipeline.ForceManualOverride();
                    }
                    else if (key == ConsoleKey.C)
                    {
                        // Toggle Crossfader Position for demo
                        masterMixer.Crossfader.Position = masterMixer.Crossfader.Position < 0.5f ? 1.0f : 0.0f;
                        Console.WriteLine($"\n[MIXER] Crossfader moved to: {masterMixer.Crossfader.Position}");
                    }
                    else
                    {
                        break;
                    }
                }
                Thread.Sleep(100);
            }

            captureService.Stop();
            masterMixer.Dispose();
            midiService.Stop();
            intentListener.Stop();
        }
    }
}
