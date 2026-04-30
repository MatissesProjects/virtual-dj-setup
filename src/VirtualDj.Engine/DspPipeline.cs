using System;
using System.Linq;
using NAudio.Dsp;
using NAudio.Wave;

namespace VirtualDj.Engine
{
    public class DspPipeline
    {
        private readonly int _fftSize;
        private readonly int _m;
        private readonly Complex[] _fftBuffer;
        private readonly float[] _sampleBuffer;
        private int _bufferOffset;

        public event EventHandler<FeatureFrame>? FeaturesCalculated;

        public DspPipeline(int fftSize = 2048)
        {
            if (!IsPowerOfTwo(fftSize))
                throw new ArgumentException("FFT size must be a power of two.");

            _fftSize = fftSize;
            _m = (int)Math.Log(fftSize, 2.0);
            _fftBuffer = new Complex[fftSize];
            _sampleBuffer = new float[fftSize];
        }

        public void ProcessSamples(float[] samples, int count, WaveFormat format)
        {
            for (int i = 0; i < count; i++)
            {
                _sampleBuffer[_bufferOffset++] = samples[i];

                if (_bufferOffset >= _fftSize)
                {
                    PerformAnalysis(format);
                    _bufferOffset = 0; // Simple non-overlapping for now, can add overlap later
                }
            }
        }

        private void PerformAnalysis(WaveFormat format)
        {
            // 1. Calculate RMS
            float sum = 0;
            for (int i = 0; i < _fftSize; i++)
            {
                sum += _sampleBuffer[i] * _sampleBuffer[i];
            }
            float rms = (float)Math.Sqrt(sum / _fftSize);

            // 2. Perform FFT
            for (int i = 0; i < _fftSize; i++)
            {
                // Apply Hanning window
                float window = (float)(0.5 * (1.0 - Math.Cos(2 * Math.PI * i / (_fftSize - 1))));
                _fftBuffer[i].X = _sampleBuffer[i] * window;
                _fftBuffer[i].Y = 0;
            }

            FastFourierTransform.FFT(true, _m, _fftBuffer);

            // 3. Extract Spectral Features
            float spectralSum = 0;
            float weightedSpectralSum = 0;
            float maxMagnitude = -1;
            int peakIndex = 0;

            int binCount = _fftSize / 2;
            float binWidth = (float)format.SampleRate / _fftSize;

            for (int i = 0; i < binCount; i++)
            {
                float magnitude = (float)Math.Sqrt(_fftBuffer[i].X * _fftBuffer[i].X + _fftBuffer[i].Y * _fftBuffer[i].Y);
                float frequency = i * binWidth;

                spectralSum += magnitude;
                weightedSpectralSum += magnitude * frequency;

                if (magnitude > maxMagnitude)
                {
                    maxMagnitude = magnitude;
                    peakIndex = i;
                }
            }

            float spectralCentroid = spectralSum > 0 ? weightedSpectralSum / spectralSum : 0;
            float peakFrequency = peakIndex * binWidth;

            FeaturesCalculated?.Invoke(this, new FeatureFrame
            {
                Rms = rms,
                SpectralCentroid = spectralCentroid,
                PeakFrequency = peakFrequency,
                Timestamp = DateTime.UtcNow
            });
        }

        private static bool IsPowerOfTwo(int n) => n > 0 && (n & (n - 1)) == 0;
    }
}
