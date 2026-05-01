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
            var dspPipeline = new DspPipeline(2048);
            var intentExecutor = new IntentExecutor(dspPipeline);
            using var midiService = new MidiService(dspPipeline);
            var playlistManager = new PlaylistManager();

            // Buffering for Track 10
            var audioBuffer = new CircularAudioBuffer(44100 * 10); // 10 seconds at 44.1k
            using var playbackService = new DeckPlaybackService(audioBuffer, captureService.WaveFormat);

            // Mock Playlist
            playlistManager.AddSong("Get Lucky", "Daft Punk");
            playlistManager.AddSong("Blinding Lights", "The Weeknd");
            playlistManager.AddSong("Levitating", "Dua Lipa");
            
            float[] floatBuffer = new float[8192];

            intentListener.IntentReceived += (intent) =>
            {
                intentExecutor.Execute(intent);
            };

            dspPipeline.FeaturesCalculated += (s, frame) =>
            {
                // 1. Write to Shared Memory for Python (passing current song index and full FFT)
                sharedMemoryService.WriteFeatureFrame(frame, 0, frame.MagnitudeSpectrum ?? Array.Empty<float>());

                // 2. Local Debug Output
                double decibels = 20 * Math.Log10(frame.Rms);
                if (double.IsInfinity(decibels)) decibels = -100;
                var song = playlistManager.CurrentSong;
                Console.Write($"\r[{song?.Title}] RMS: {decibels:F1} dB | Tempo: {playbackService.Tempo:F2}x | Auth: {frame.Authority}    ");
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

                // Write to Circular Buffer for Playback manipulation
                audioBuffer.Write(floatBuffer, sampleCount);

                dspPipeline.ProcessSamples(floatBuffer, sampleCount, captureService.WaveFormat);
            };

            intentListener.Start();
            midiService.Start();
            playbackService.Start();
            captureService.Start();

            Console.WriteLine("Press any key to stop... (Press 'M' for Manual, 'T' to increase Tempo)");
            
            while (true)
            {
                if (Console.KeyAvailable)
                {
                    var key = Console.ReadKey(true).Key;
                    if (key == ConsoleKey.M)
                    {
                        dspPipeline.ForceManualOverride();
                    }
                    else if (key == ConsoleKey.T)
                    {
                        playbackService.Tempo += 0.05f;
                    }
                    else
                    {
                        break;
                    }
                }
                Thread.Sleep(100);
            }

            captureService.Stop();
            playbackService.Stop();
            midiService.Stop();
            intentListener.Stop();
        }
    }
}
