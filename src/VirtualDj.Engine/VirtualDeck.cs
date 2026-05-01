using System;
using NAudio.Wave;

namespace VirtualDj.Engine
{
    public class VirtualDeck
    {
        public string Name { get; }
        public CircularAudioBuffer Buffer { get; }
        public DspPipeline Pipeline { get; }
        public DeckPlaybackService Playback { get; }

        public VirtualDeck(string name, WaveFormat format)
        {
            Name = name;
            Buffer = new CircularAudioBuffer(format.SampleRate * 10); // 10s
            Pipeline = new DspPipeline(2048);
            Playback = new DeckPlaybackService(Buffer, format);
        }

        public void Process(float[] samples, int count, WaveFormat format)
        {
            Buffer.Write(samples, count);
            Pipeline.ProcessSamples(samples, count, format);
        }
    }
}
