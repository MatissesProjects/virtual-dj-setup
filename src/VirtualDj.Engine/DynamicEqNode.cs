using System;
using NAudio.Dsp;

namespace VirtualDj.Engine
{
    public class DynamicEqNode
    {
        private BiQuadFilter? _filter;
        private float _gainDb = 0;
        private float _frequency = 1000;
        private float _q = 1.0f;
        private int _sampleRate;

        public float GainDb
        {
            get => _gainDb;
            set { _gainDb = value; UpdateFilter(); }
        }

        public float Frequency
        {
            get => _frequency;
            set { _frequency = value; UpdateFilter(); }
        }

        public void Initialize(int sampleRate)
        {
            _sampleRate = sampleRate;
            UpdateFilter();
        }

        private void UpdateFilter()
        {
            if (_sampleRate > 0)
            {
                _filter = BiQuadFilter.PeakingEQ(_sampleRate, _frequency, _q, _gainDb);
            }
        }

        public void Process(float[] samples, int count)
        {
            if (_filter == null) return;
            for (int i = 0; i < count; i++)
            {
                samples[i] = _filter.Transform(samples[i]);
            }
        }
    }
}
