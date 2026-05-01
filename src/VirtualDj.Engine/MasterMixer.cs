using System;
using NAudio.Wave;

namespace VirtualDj.Engine
{
    public class MasterMixer : IWaveProvider, IDisposable
    {
        private readonly VirtualDeck _deckA;
        private readonly VirtualDeck _deckB;
        private readonly Crossfader _crossfader;
        private readonly WaveFormat _format;
        private readonly WasapiOut _output;

        public MasterMixer(VirtualDeck deckA, VirtualDeck deckB, WaveFormat format)
        {
            _deckA = deckA;
            _deckB = deckB;
            _format = format;
            _crossfader = new Crossfader();
            
            _output = new WasapiOut(NAudio.CoreAudioApi.AudioClientShareMode.Shared, 20);
            _output.Init(this);
        }

        public Crossfader Crossfader => _crossfader;

        public void Start() => _output.Play();
        public void Stop() => _output.Stop();

        public int Read(byte[] buffer, int offset, int count)
        {
            int samplesRequired = count / 4;
            var waveBuffer = new WaveBuffer(buffer);
            
            float[] bufferA = new float[samplesRequired];
            float[] bufferB = new float[samplesRequired];

            // Read from both decks
            int readA = _deckA.Playback.Read(bufferA, 0, samplesRequired);
            int readB = _deckB.Playback.Read(bufferB, 0, samplesRequired);

            // Mix through crossfader
            _crossfader.Process(bufferA, bufferB, waveBuffer.FloatBuffer, samplesRequired);
            
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
