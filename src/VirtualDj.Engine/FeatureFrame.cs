using System.Numerics;

namespace VirtualDj.Engine
{
    public struct FeatureFrame
    {
        public float Rms { get; set; }
        public float SpectralCentroid { get; set; }
        public float PeakFrequency { get; set; }
        public float[]? MagnitudeSpectrum { get; set; } // Optional for detailed viz
        public DateTime Timestamp { get; set; }
    }
}
