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

        private readonly CompressorNode _compressor = new CompressorNode();
        private readonly LimiterNode _limiter = new LimiterNode();
        private readonly StereoWidthNode _widthNode = new StereoWidthNode();

        public event EventHandler<FeatureFrame>? FeaturesCalculated;

        public DspPipeline(int fftSize = 2048)
        {
            if (!IsPowerOfTwo(fftSize))
                throw new ArgumentException("FFT size must be a power of two.");

            _fftSize = fftSize;
            _m = (int)Math.Log(fftSize, 2.0);
            _fftBuffer = new Complex[fftSize];
            _sampleBuffer = new float[fftSize];
            
            _compressor.Threshold = 0.4f;
            _compressor.Ratio = 2.0f;
            _compressor.AttackMs = 20.0f;
            _compressor.ReleaseMs = 200.0f;
            _compressor.MakeUpGain = 1.2f;

            _widthNode.Width = 1.2f; // Slight stereo enhancement by default
        }

        public void ProcessSamples(float[] samples, int count, WaveFormat format)
        {
            // 1. Professional DSP Chain (Dynamics & Stereo)
            if (format.Channels == 2)
            {
                // De-interleave for stereo/MS processing
                int frameCount = count / 2;
                float[] left = new float[frameCount];
                float[] right = new float[frameCount];
                
                for (int i = 0; i < frameCount; i++)
                {
                    left[i] = samples[i * 2];
                    right[i] = samples[i * 2 + 1];
                }

                _widthNode.Process(left, right, frameCount);

                // Re-interleave for dynamics (simplified linked processing)
                for (int i = 0; i < frameCount; i++)
                {
                    samples[i * 2] = left[i];
                    samples[i * 2 + 1] = right[i];
                }
            }

            _compressor.Process(samples, count, format.SampleRate);
            _limiter.Process(samples, count, format.SampleRate);

            // 2. Buffer for analysis (using mono-summed for FFT)
            for (int i = 0; i < count; i += format.Channels)
            {
                float mono = 0;
                for (int c = 0; c < format.Channels; c++) mono += samples[i + c];
                mono /= format.Channels;

                _sampleBuffer[_bufferOffset++] = mono;

                if (_bufferOffset >= _fftSize)
                {
                    PerformAnalysis(format);
                    _bufferOffset = 0;
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
