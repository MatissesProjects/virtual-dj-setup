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
        private readonly NetworkAudioBridge _networkBridge;
        private readonly WaveFormat _format;
        private readonly WasapiOut _output;

        public bool UseRemoteAi { get; set; } = false;

        public MasterMixer(VirtualDeck deckA, VirtualDeck deckB, WaveFormat format, string remoteAiIp = "127.0.0.1")
        {
            _deckA = deckA;
            _deckB = deckB;
            _format = format;
            _crossfader = new Crossfader();
            _audioBridge = new SharedAudioBridge();
            _networkBridge = new NetworkAudioBridge(remoteAiIp);
            
            _output = new WasapiOut(NAudio.CoreAudioApi.AudioClientShareMode.Shared, 20);
            _output.Init(this);
        }

        public Crossfader Crossfader => _crossfader;
        public SharedAudioBridge AudioBridge => _audioBridge;
        public NetworkAudioBridge NetworkBridge => _networkBridge;

        public void Start() 
        {
            if (UseRemoteAi) _networkBridge.Connect();
            _output.Play();
        }

        public void Stop() => _output.Stop();

        private readonly float[] _stemVocal = new float[2048];
        private readonly float[] _stemDrums = new float[2048];
        private readonly float[] _stemBass = new float[2048];
        private readonly float[] _stemOther = new float[2048];

        public (float Vocal, float Drums, float Bass, float Other) StemVolumes { get; set; } = (1.0f, 1.0f, 1.0f, 1.0f);
        public bool StemsActive { get; set; } = true; // Assume active for Track 15 prototype

        public int Read(byte[] buffer, int offset, int count)
        {
            int samplesRequired = count / 4;
            var waveBuffer = new WaveBuffer(buffer);
            
            float[] bufferA = new float[samplesRequired];
            float[] bufferB = new float[samplesRequired];

            // 1. Read from both decks
            int readA = _deckA.Playback.Read(bufferA, 0, samplesRequired);
            int readB = _deckB.Playback.Read(bufferB, 0, samplesRequired);

            // 2. Neural Bridge (Local or Remote)
            if (UseRemoteAi && _networkBridge.IsConnected)
            {
                _networkBridge.SendInput(bufferA, samplesRequired);
                Buffer.BlockCopy(_networkBridge.GetStem(1), 0, _stemVocal, 0, samplesRequired * 4);
                Buffer.BlockCopy(_networkBridge.GetStem(2), 0, _stemDrums, 0, samplesRequired * 4);
                Buffer.BlockCopy(_networkBridge.GetStem(3), 0, _stemBass, 0, samplesRequired * 4);
                Buffer.BlockCopy(_networkBridge.GetStem(4), 0, _stemOther, 0, samplesRequired * 4);
            }
            else
            {
                _audioBridge.WriteInput(bufferA, samplesRequired);
                _audioBridge.ReadStem(1, _stemVocal, samplesRequired);
                _audioBridge.ReadStem(2, _stemDrums, samplesRequired);
                _audioBridge.ReadStem(3, _stemBass, samplesRequired);
                _audioBridge.ReadStem(4, _stemOther, samplesRequired);
            }

            // Optional: Reconstruct Deck A from stems if Stem separation is active and modifying volumes
            if (StemsActive)
            {
                for (int i = 0; i < samplesRequired; i++)
                {
                    // If stems are empty (Python not running), this will mute Deck A.
                    // A real app would fallback to original bufferA if stems are empty.
                    float reconstructed = 
                        (_stemVocal[i] * StemVolumes.Vocal) + 
                        (_stemDrums[i] * StemVolumes.Drums) + 
                        (_stemBass[i] * StemVolumes.Bass) + 
                        (_stemOther[i] * StemVolumes.Other);
                    
                    // Simple fallback: if all stems are exactly 0, keep original bufferA
                    if (_stemVocal[i] == 0 && _stemDrums[i] == 0 && _stemBass[i] == 0 && _stemOther[i] == 0)
                        continue; 

                    bufferA[i] = reconstructed;
                }
            }

            // 3. Mix through crossfader
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
