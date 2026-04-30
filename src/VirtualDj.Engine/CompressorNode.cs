using System;

namespace VirtualDj.Engine
{
    public class CompressorNode
    {
        public float Threshold { get; set; } = 0.5f; // 0.0 to 1.0
        public float Ratio { get; set; } = 4.0f;
        public float AttackMs { get; set; } = 10.0f;
        public float ReleaseMs { get; set; } = 100.0f;
        public float MakeUpGain { get; set; } = 1.0f;

        private float _currentGain = 1.0f;
        private float _envelope = 0.0f;

        public void Process(float[] samples, int count, int sampleRate)
        {
            float attackCoef = (float)Math.Exp(-1.0 / (sampleRate * AttackMs / 1000.0));
            float releaseCoef = (float)Math.Exp(-1.0 / (sampleRate * ReleaseMs / 1000.0));

            for (int i = 0; i < count; i++)
            {
                float input = Math.Abs(samples[i]);
                
                // Envelope detection (RMS-ish peak follow)
                if (input > _envelope)
                    _envelope = attackCoef * _envelope + (1.0f - attackCoef) * input;
                else
                    _envelope = releaseCoef * _envelope + (1.0f - releaseCoef) * input;

                // Compression logic
                float targetGain = 1.0f;
                if (_envelope > Threshold && _envelope > 0)
                {
                    // standard compression formula: 1 - (1 - (T/E)) * (1 - 1/R)
                    // Simplified: (Threshold + (Envelope - Threshold) / Ratio) / Envelope
                    targetGain = (Threshold + (_envelope - Threshold) / Ratio) / _envelope;
                }

                _currentGain = targetGain; // In a more advanced version, we'd smooth this too
                samples[i] *= _currentGain * MakeUpGain;
            }
        }

        public float LastGainReduction => 1.0f - _currentGain;
    }
}
