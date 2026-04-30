using System.IO.MemoryMappedFiles;

namespace VirtualDj.Engine
{
    public class SharedMemoryService : IDisposable
    {
        private const string MapName = "VirtualDjFeatures";
        private const int FFTBinCount = 1024;
        // Header (40 bytes) + FFT Data (1024 * 4 bytes)
        private const int BufferSize = 40 + (FFTBinCount * 4); 
        
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
            _accessor.Write(36, 0); // IsPeak placeholder for now
            
            // Write FFT Array
            if (fftMagnitudes != null && fftMagnitudes.Length >= FFTBinCount)
            {
                _accessor.WriteArray(40, fftMagnitudes, 0, FFTBinCount);
            }

            // 3. Release Lock Byte
            _accessor.Write(4, 0); 
        }

        public void Dispose()
        {
            _accessor.Dispose();
            _mmf.Dispose();
        }
    }
}
