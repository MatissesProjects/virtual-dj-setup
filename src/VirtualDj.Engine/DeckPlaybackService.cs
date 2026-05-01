using System;
using NAudio.Wave;

namespace VirtualDj.Engine
{
    public class DeckPlaybackService : ISampleProvider
    {
        private readonly CircularAudioBuffer _buffer;
        private readonly WaveFormat _format;
        private double _readPos;
        private float _tempo = 1.0f;

        public DeckPlaybackService(CircularAudioBuffer buffer, WaveFormat format)
        {
            _buffer = buffer;
            _format = format;
        }

        public float Tempo
        {
            get => _tempo;
            set => _tempo = value;
        }

        public int Read(float[] buffer, int offset, int count)
        {
            float[] temp = new float[1];
            
            for (int i = 0; i < count; i++)
            {
                _buffer.Read(temp, (long)_readPos, 1);
                buffer[offset + i] = temp[0];
                _readPos += _tempo;
            }

            return count;
        }

        public WaveFormat WaveFormat => _format;
    }
}
