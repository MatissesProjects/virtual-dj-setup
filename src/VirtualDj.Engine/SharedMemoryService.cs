using System.IO.MemoryMappedFiles;
using System.Threading;

namespace VirtualDj.Engine
{
    public class SharedMemoryService : IDisposable
    {
        private const string MapName = "VirtualDjFeatures";
        private const int FFTBinCount = 1024;
        
        // Ring Buffer Constants
        private const int BufferSlots = 4;
        private const int HeaderSize = 64;
        private const int SlotSize = HeaderSize + (FFTBinCount * 4); // ~4.1KB per slot
        
        // Shared State layout:
        // [0-3] WritePointer (Int32, atomically updated)
        // [4-7] IsDone (Int32)
        // [8-11] StepCommand (Int32)
        // [12-15] StepSize (Int32)
        // [16-19] DuckFreq (Float)
        // [20-23] DuckGain (Float)
        // [24-27] CrossfaderPos (Float)
        // [64..] Ring Buffer Slots (SlotSize * BufferSlots)
        private const int StateOffset = 0;
        private const int SlotsOffset = 64;
        private const int TotalBufferSize = SlotsOffset + (SlotSize * BufferSlots); 
        
        private readonly MemoryMappedFile _mmf;
        private readonly MemoryMappedViewAccessor _accessor;
        private int _sequenceNumber = 0;

        public SharedMemoryService()
        {
            _mmf = MemoryMappedFile.CreateOrOpen(MapName, TotalBufferSize);
            _accessor = _mmf.CreateViewAccessor();
        }

        public void WriteCrossfaderPosition(float pos)
        {
            _accessor.Write(StateOffset + 24, pos);
        }

        public float ReadCrossfaderPosition()
        {
            return _accessor.ReadSingle(StateOffset + 24);
        }

        public (float vocal, float drums, float bass, float other) ReadStemVolumes()
        {
            float vocal = _accessor.ReadSingle(StateOffset + 28);
            float drums = _accessor.ReadSingle(StateOffset + 32);
            float bass = _accessor.ReadSingle(StateOffset + 36);
            float other = _accessor.ReadSingle(StateOffset + 40);
            
            // If completely uninitialized (0s across the board), default to 1.0
            if (vocal == 0 && drums == 0 && bass == 0 && other == 0)
                return (1.0f, 1.0f, 1.0f, 1.0f);
                
            return (vocal, drums, bass, other);
        }

        private readonly object _writeLock = new object();

        public void WriteFeatureFrame(FeatureFrame frame, int deckIndex, float[] fftMagnitudes)
        {
            lock (_writeLock)
            {
                // 1. Determine which slot to write to (next available)
                int currentWritePtr = _accessor.ReadInt32(StateOffset);
                int nextSlot = (currentWritePtr + 1) % BufferSlots;
                int offset = SlotsOffset + (nextSlot * SlotSize);

                // 2. Write Data to the *next* slot
                _accessor.Write(offset + 0, ++_sequenceNumber);
                _accessor.Write(offset + 4, frame.Rms);
                _accessor.Write(offset + 8, frame.SpectralCentroid);
                _accessor.Write(offset + 12, frame.PeakFrequency);
                _accessor.Write(offset + 16, (int)frame.Authority);
                _accessor.Write(offset + 20, deckIndex); // Used as Deck Index
                _accessor.Write(offset + 24, frame.Timestamp.ToBinary());
                _accessor.Write(offset + 32, 0); // IsPeak placeholder
                
                // Write FFT Array
                if (fftMagnitudes != null && fftMagnitudes.Length >= FFTBinCount)
                {
                    _accessor.WriteArray(offset + 64, fftMagnitudes, 0, FFTBinCount);
                }

                // 3. Commit the write
                _accessor.Write(StateOffset, nextSlot); 
            }
        }

        // Gym Synchronization Methods
        public void WriteIsDone(bool isDone)
        {
            _accessor.Write(StateOffset + 4, isDone ? 1 : 0);
        }

        public (int command, int size) ReadStepCommand()
        {
            int command = _accessor.ReadInt32(StateOffset + 8);
            int size = _accessor.ReadInt32(StateOffset + 12);
            return (command, size);
        }

        public void ClearStepCommand()
        {
            _accessor.Write(StateOffset + 8, 0);
        }

        public void UpdateDuckingParams(float freq, float gain)
        {
            _accessor.Write(StateOffset + 16, freq);
            _accessor.Write(StateOffset + 20, gain);
        }

        public (float freq, float gain) ReadDuckingParams()
        {
            float freq = _accessor.ReadSingle(StateOffset + 16);
            float gain = _accessor.ReadSingle(StateOffset + 20);
            return (freq, gain);
        }

        public void Dispose()
        {
            _accessor.Dispose();
            _mmf.Dispose();
        }
    }
}
