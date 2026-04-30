using System;

namespace VirtualDj.Engine
{
    public class SplineInterpolator
    {
        private float _startValue;
        private float _endValue;
        private long _durationSamples;
        private long _elapsedSamples;
        private bool _isActive;

        public float CurrentValue { get; private set; }

        public void Start(float start, float end, long durationSamples)
        {
            _startValue = start;
            _endValue = end;
            _durationSamples = durationSamples;
            _elapsedSamples = 0;
            _isActive = true;
            CurrentValue = start;
        }

        public float NextSample()
        {
            if (!_isActive) return _endValue;

            _elapsedSamples++;
            if (_elapsedSamples >= _durationSamples)
            {
                _isActive = false;
                CurrentValue = _endValue;
                return _endValue;
            }

            // Simple Linear for now (can upgrade to Bezier/Spline)
            float t = (float)_elapsedSamples / _durationSamples;
            CurrentValue = _startValue + (_endValue - _startValue) * t;
            
            return CurrentValue;
        }

        public bool IsActive => _isActive;
    }
}
