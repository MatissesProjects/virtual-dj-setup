using System.IO.MemoryMappedFiles;

namespace VirtualDj.Engine
{
    public class SharedMemoryService : IDisposable
    {
        private const string MapName = "VirtualDjFeatures";
        private const int BufferSize = 1024; // Large enough for our struct
        private readonly MemoryMappedFile _mmf;
        private readonly MemoryMappedViewAccessor _accessor;

        public SharedMemoryService()
        {
            _mmf = MemoryMappedFile.CreateOrOpen(MapName, BufferSize);
            _accessor = _mmf.CreateViewAccessor();
        }

        public void WriteFeatureFrame(FeatureFrame frame, int songIndex)
        {
            // Simple binary write
            _accessor.Write(0, frame.Rms);
            _accessor.Write(4, frame.SpectralCentroid);
            _accessor.Write(8, frame.PeakFrequency);
            _accessor.Write(12, (int)frame.Authority);
            _accessor.Write(16, songIndex); // New field
            _accessor.Write(20, frame.Timestamp.ToBinary());
        }

        public void Dispose()
        {
            _accessor.Dispose();
            _mmf.Dispose();
        }
    }
}
