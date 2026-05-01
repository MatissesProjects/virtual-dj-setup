using System;

namespace VirtualDj.Engine
{
    public class CircularAudioBuffer
    {
        private readonly float[] _buffer;
        private long _writePos;
        private readonly int _size;

        public CircularAudioBuffer(int sizeInSamples)
        {
            _size = sizeInSamples;
            _buffer = new float[_size];
        }

        public void Write(float[] samples, int count)
        {
            for (int i = 0; i < count; i++)
            {
                _buffer[_writePos % _size] = samples[i];
                _writePos++;
            }
        }

        public void Read(float[] dest, long startSample, int count)
        {
            for (int i = 0; i < count; i++)
            {
                dest[i] = _buffer[(startSample + i) % _size];
            }
        }

        public long CurrentWritePos => _writePos;
        public int Size => _size;
    }
}
