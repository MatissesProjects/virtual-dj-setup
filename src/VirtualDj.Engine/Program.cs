using System;
using NAudio.Wave;

namespace VirtualDj.Engine
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Virtual DJ Engine starting...");

            using var captureService = new WasapiCaptureService();
            using var sharedMemoryService = new SharedMemoryService();
            using var intentListener = new IntentListener();
            
            // Track 11: Multi-Deck Support
            using var deckA = new VirtualDeck("Deck A", captureService.WaveFormat);
            // using var deckB = new VirtualDeck("Deck B", captureService.WaveFormat); // Ready for future
            
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

                // 2. Read Ducking Commands from Python (Bi-directional MMF)
                var (freq, gain) = sharedMemoryService.ReadDuckingParams();
                if (freq > 0)
                {
                    deckA.Pipeline.SetDucking(freq, gain);
                }

                // 3. Local Debug Output
                double decibels = 20 * Math.Log10(frame.Rms);
                if (double.IsInfinity(decibels)) decibels = -100;
                var song = playlistManager.CurrentSong;
                Console.Write($"\r[{song?.Title}] RMS: {decibels:F1} dB | Tempo: {deckA.Playback.Tempo:F2}x | Auth: {frame.Authority}    ");
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

                // Process through Deck A
                deckA.Process(floatBuffer, sampleCount, captureService.WaveFormat);
            };

            intentListener.Start();
            midiService.Start();
            deckA.Playback.Start();
            captureService.Start();

            Console.WriteLine("Press any key to stop... (Press 'M' for Manual, 'T' to increase Tempo)");
            
            while (true)
            {
                if (Console.KeyAvailable)
                {
                    var key = Console.ReadKey(true).Key;
                    if (key == ConsoleKey.M)
                    {
                        deckA.Pipeline.ForceManualOverride();
                    }
                    else if (key == ConsoleKey.T)
                    {
                        deckA.Playback.Tempo += 0.05f;
                    }
                    else
                    {
                        break;
                    }
                }
                Thread.Sleep(100);
            }

            captureService.Stop();
            deckA.Dispose();
            midiService.Stop();
            intentListener.Stop();
        }
    }
}
