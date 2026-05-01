using System;
using NAudio.Wave;

namespace VirtualDj.Engine
{
    public class MasterMixer : IWaveProvider, IDisposable
    {
        private readonly VirtualDeck _deckA;
        private readonly VirtualDeck _deckB;
        private readonly Crossfader _crossfader;
        private readonly SharedAudioBridge _audioBridge;
        private readonly WaveFormat _format;
        private readonly WasapiOut _output;

        public MasterMixer(VirtualDeck deckA, VirtualDeck deckB, WaveFormat format)
        {
            _deckA = deckA;
            _deckB = deckB;
            _format = format;
            _crossfader = new Crossfader();
            _audioBridge = new SharedAudioBridge();
            
            _output = new WasapiOut(NAudio.CoreAudioApi.AudioClientShareMode.Shared, 20);
            _output.Init(this);
        }

        public Crossfader Crossfader => _crossfader;
        public SharedAudioBridge AudioBridge => _audioBridge;

        public void Start() => _output.Play();
        public void Stop() => _output.Stop();

        private readonly float[] _stemVocal = new float[2048];
        private readonly float[] _stemDrums = new float[2048];
        private readonly float[] _stemBass = new float[2048];
        private readonly float[] _stemOther = new float[2048];

        public int Read(byte[] buffer, int offset, int count)
        {
            int samplesRequired = count / 4;
            var waveBuffer = new WaveBuffer(buffer);
            
            float[] bufferA = new float[samplesRequired];
            float[] bufferB = new float[samplesRequired];

            // 1. Read from both decks
            int readA = _deckA.Playback.Read(bufferA, 0, samplesRequired);
            int readB = _deckB.Playback.Read(bufferB, 0, samplesRequired);

            // 2. Stream Deck A to Python for Stem Separation (The "Neural Bridge")
            _audioBridge.WriteInput(bufferA, samplesRequired);

            // 3. Read Stems back from Python (with optional fallback)
            // Note: In a production scenario, we'd use a jitter buffer here.
            _audioBridge.ReadStem(1, _stemVocal, samplesRequired);
            _audioBridge.ReadStem(2, _stemDrums, samplesRequired);
            _audioBridge.ReadStem(3, _stemBass, samplesRequired);
            _audioBridge.ReadStem(4, _stemOther, samplesRequired);

            // 4. Mix through crossfader
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
