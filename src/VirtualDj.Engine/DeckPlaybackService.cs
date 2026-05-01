using System;
using NAudio.Wave;

namespace VirtualDj.Engine
{
    public class DeckPlaybackService : IWaveProvider, IDisposable
    {
        private readonly CircularAudioBuffer _buffer;
        private readonly WaveFormat _format;
        private long _readPos;
        private float _tempo = 1.0f;
        private readonly WasapiOut _output;

        public DeckPlaybackService(CircularAudioBuffer buffer, WaveFormat format)
        {
            _buffer = buffer;
            _format = format;
            _output = new WasapiOut(NAudio.CoreAudioApi.AudioClientShareMode.Shared, 20);
            _output.Init(this);
        }

        public void Start() => _output.Play();
        public void Stop() => _output.Stop();

        public float Tempo
        {
            get => _tempo;
            set => _tempo = value;
        }

        public int Read(byte[] buffer, int offset, int count)
        {
            int samplesRequired = count / 4;
            var waveBuffer = new WaveBuffer(buffer);
            
            float[] temp = new float[samplesRequired];
            
            // Basic resampling/speed change for now
            // readPos advances at a different rate than the output clock
            for (int i = 0; i < samplesRequired; i++)
            {
                // Simple linear interpolation could be added here
                _buffer.Read(temp, (long)_readPos, 1);
                waveBuffer.FloatBuffer[offset / 4 + i] = temp[0];
                _readPos = (long)(_readPos + 1 * _tempo); // This is very naive, but proves the speed mod
            }

            return count;
        }

        public WaveFormat WaveFormat => _format;

        public void Dispose()
        {
            _output.Stop();
            _output.Dispose();
        }
    }
}
