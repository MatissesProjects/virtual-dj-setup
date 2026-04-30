using System;

namespace VirtualDj.Engine
{
    public class LimiterNode
    {
        public float Ceiling { get; set; } = 0.95f; // -0.5 dB roughly
        public float ReleaseMs { get; set; } = 50.0f;

        private float _currentGain = 1.0f;

        public void Process(float[] samples, int count, int sampleRate)
        {
            float releaseCoef = (float)Math.Exp(-1.0 / (sampleRate * ReleaseMs / 1000.0));

            for (int i = 0; i < count; i++)
            {
                float input = Math.Abs(samples[i]);
                float targetGain = 1.0f;

                if (input * _currentGain > Ceiling)
                {
                    targetGain = Ceiling / input;
                }

                // Smoothly return to 1.0, but react instantly to peaks
                if (targetGain < _currentGain)
                    _currentGain = targetGain;
                else
                    _currentGain = releaseCoef * _currentGain + (1.0f - releaseCoef) * 1.0f;

                samples[i] *= _currentGain;
                
                // Hard clip just in case
                if (samples[i] > 1.0f) samples[i] = 1.0f;
                if (samples[i] < -1.0f) samples[i] = -1.0f;
            }
        }
    }
}
