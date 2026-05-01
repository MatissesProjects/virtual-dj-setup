using System.IO.MemoryMappedFiles;

namespace VirtualDj.Engine
{
    public class SharedMemoryService : IDisposable
    {
        private const string MapName = "VirtualDjFeatures";
        private const int FFTBinCount = 1024;
        private const int BufferSize = 64 + (FFTBinCount * 4); // Expanded for future growth
        
        private readonly MemoryMappedFile _mmf;
        private readonly MemoryMappedViewAccessor _accessor;
        private int _sequenceNumber = 0;

        public SharedMemoryService()
        {
            _mmf = MemoryMappedFile.CreateOrOpen(MapName, BufferSize);
            _accessor = _mmf.CreateViewAccessor();
        }

        public void WriteFeatureFrame(FeatureFrame frame, int songIndex, float[] fftMagnitudes)
        {
            // 1. Set Lock Byte
            _accessor.Write(4, 1); 

            // 2. Write Data
            _accessor.Write(0, ++_sequenceNumber);
            _accessor.Write(8, frame.Rms);
            _accessor.Write(12, frame.SpectralCentroid);
            _accessor.Write(16, frame.PeakFrequency);
            _accessor.Write(20, (int)frame.Authority);
            _accessor.Write(24, songIndex);
            _accessor.Write(28, frame.Timestamp.ToBinary());
            _accessor.Write(36, 0); // IsPeak placeholder
            _accessor.Write(40, 0f); // Ducking Frequency (Read from here)
            _accessor.Write(44, 0f); // Ducking Gain (Read from here)
            
            // Write FFT Array
            if (fftMagnitudes != null && fftMagnitudes.Length >= FFTBinCount)
            {
                _accessor.WriteArray(48, fftMagnitudes, 0, FFTBinCount);
            }

            // 3. Release Lock Byte
            _accessor.Write(4, 0); 
        }

        public void UpdateDuckingParams(float freq, float gain)
        {
            _accessor.Write(40, freq);
            _accessor.Write(44, gain);
        }

        public (float freq, float gain) ReadDuckingParams()
        {
            float freq = _accessor.ReadSingle(40);
            float gain = _accessor.ReadSingle(44);
            return (freq, gain);
        }

        public void Dispose()
        {
            _accessor.Dispose();
            _mmf.Dispose();
        }
    }
}
