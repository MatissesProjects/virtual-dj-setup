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
            
            captureService.DataAvailable += (s, e) =>
            {
                float max = 0;
                var buffer = new WaveBuffer(e.Buffer);
                // interpreted as float since WASAPI loopback is usually 32-bit float
                for (int index = 0; index < e.BytesRecorded / 4; index++)
                {
                    var sample = buffer.FloatBuffer[index];
                    if (sample < 0) sample = -sample;
                    if (sample > max) max = sample;
                }
                
                // Calculate RMS (simple version for visualization)
                double sum = 0;
                for (int index = 0; index < e.BytesRecorded / 4; index++)
                {
                    var sample = buffer.FloatBuffer[index];
                    sum += sample * sample;
                }
                double rms = Math.Sqrt(sum / (e.BytesRecorded / 4));
                double decibels = 20 * Math.Log10(rms);

                if (double.IsInfinity(decibels)) decibels = -100;

                // Print a small bar
                int barLength = (int)((decibels + 60) / 60 * 50);
                if (barLength < 0) barLength = 0;
                if (barLength > 50) barLength = 50;

                Console.Write($"\rRMS: {decibels:F2} dB |{new string('#', barLength)}{new string('-', 50 - barLength)}|");
            };

            captureService.Start();

            Console.WriteLine("Press any key to stop...");
            Console.ReadKey();

            captureService.Stop();
        }
    }
}
