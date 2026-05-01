using System;

namespace VirtualDj.Engine
{
    public enum CrossfaderCurve
    {
        Linear,
        EqualPower
    }

    public class Crossfader
    {
        private float _manualPosition = 0.5f;
        private readonly SplineInterpolator _interpolator = new SplineInterpolator();

        public float Position 
        { 
            get => _interpolator.IsActive ? _interpolator.CurrentValue : _manualPosition;
            set 
            {
                if (!_interpolator.IsActive)
                    _manualPosition = value;
            }
        }

        public CrossfaderCurve Curve { get; set; } = CrossfaderCurve.EqualPower;

        public void Automate(float target, int durationMs, int sampleRate)
        {
            _interpolator.Start(Position, target, (long)durationMs * sampleRate / 1000);
        }

        public void Process(float[] deckASamples, float[] deckBSamples, float[] outputSamples, int count)
        {
            for (int i = 0; i < count; i++)
            {
                float currentPos = _interpolator.IsActive ? _interpolator.NextSample() : _manualPosition;
                float gainA, gainB;

                if (Curve == CrossfaderCurve.Linear)
                {
                    gainA = 1.0f - currentPos;
                    gainB = currentPos;
                }
                else // Equal Power
                {
                    gainA = (float)Math.Cos(currentPos * Math.PI * 0.5);
                    gainB = (float)Math.Sin(currentPos * Math.PI * 0.5);
                }

                outputSamples[i] = (deckASamples[i] * gainA) + (deckBSamples[i] * gainB);
            }
        }
    }
}
