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
            var dspPipeline = new DspPipeline(2048);
            
            float[] floatBuffer = new float[8192];

            dspPipeline.FeaturesCalculated += (s, frame) =>
            {
                // 1. Write to Shared Memory for Python
                sharedMemoryService.WriteFeatureFrame(frame);

                // 2. Local Debug Output
                double decibels = 20 * Math.Log10(frame.Rms);
                if (double.IsInfinity(decibels)) decibels = -100;
                Console.Write($"\rRMS: {decibels:F1} dB | Centroid: {frame.SpectralCentroid:F0} Hz | Peak: {frame.PeakFrequency:F0} Hz    ");
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

                dspPipeline.ProcessSamples(floatBuffer, sampleCount, captureService.WaveFormat);
            };

            captureService.Start();

            Console.WriteLine("Press any key to stop...");
            Console.ReadKey();

            captureService.Stop();
        }
    }
}
