using System;
using System.IO.MemoryMappedFiles;

namespace VirtualDj.Engine
{
    /// <summary>
    /// Manages high-bandwidth PCM audio streaming between C# and Python using MMF.
    /// Supports a 1024-sample stereo block (4096 bytes + header).
    /// </summary>
    public class SharedAudioBridge : IDisposable
    {
        private const string MapName = "VirtualDjAudioBridge";
        private const int SampleRate = 44100;
        private const int BlockSize = 1024; // Samples per block
        private const int Channels = 2;
        
        // Header: [0-3] WritePtr (Int32), [4-7] ReadPtr (Int32), [8-11] Seq (Int32)
        private const int HeaderSize = 64;
        private const int AudioDataSize = BlockSize * Channels * sizeof(float);
        
        // Stems: Input, Vocal, Drum, Bass, Other, Bridge (6 discrete streams)
        private const int StreamCount = 6;
        private const int StreamSize = HeaderSize + AudioDataSize;
        private const int TotalBufferSize = StreamSize * StreamCount;

        private readonly MemoryMappedFile _mmf;
        private readonly MemoryMappedViewAccessor _accessor;
        private int _sequence = 0;

        public SharedAudioBridge()
        {
            _mmf = MemoryMappedFile.CreateOrOpen(MapName, TotalBufferSize);
            _accessor = _mmf.CreateViewAccessor();
        }

        /// <summary>
        /// Writes a block of audio for Python to process.
        /// </summary>
        public void WriteInput(float[] samples, int count)
        {
            int offset = 0 * StreamSize; // Stream 0 is Input
            _accessor.WriteArray(offset + HeaderSize, samples, 0, Math.Min(count, BlockSize * Channels));
            _accessor.Write(offset + 8, ++_sequence); // Update sequence to signal new data
        }

        /// <summary>
        /// Reads a specific stem from Python.
        /// stemIndex: 1=Vocal, 2=Drum, 3=Bass, 4=Other, 5=Bridge
        /// </summary>
        public int ReadStem(int stemIndex, float[] buffer, int count)
        {
            if (stemIndex < 1 || stemIndex > 5) return 0;
            
            int offset = stemIndex * StreamSize;
            int seq = _accessor.ReadInt32(offset + 8);
            
            _accessor.ReadArray(offset + HeaderSize, buffer, 0, Math.Min(count, BlockSize * Channels));
            return count;
        }

        public void Dispose()
        {
            _accessor.Dispose();
            _mmf.Dispose();
        }
    }
}
