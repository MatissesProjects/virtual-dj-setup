using System;
using NAudio.Midi;

namespace VirtualDj.Engine
{
    public class MidiService : IDisposable
    {
        private MidiIn? _midiIn;
        private readonly DspPipeline _pipeline;

        public MidiService(DspPipeline pipeline)
        {
            _pipeline = pipeline;
        }

        public void Start()
        {
            if (MidiIn.NumberOfDevices == 0)
            {
                Console.WriteLine("[MIDI] No MIDI input devices found.");
                return;
            }

            try
            {
                _midiIn = new MidiIn(0); // Use the first available device
                _midiIn.MessageReceived += OnMessageReceived;
                _midiIn.ErrorReceived += OnErrorReceived;
                _midiIn.Start();
                Console.WriteLine($"[MIDI] Started listening on: {MidiIn.DeviceInfo(0).ProductName}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[MIDI] Error starting device: {ex.Message}");
            }
        }

        private void OnMessageReceived(object? sender, MidiInMessageEventArgs e)
        {
            if (e.MidiEvent.CommandCode == MidiCommandCode.ControlChange)
            {
                var cc = (ControlChangeEvent)e.MidiEvent;
                
                // Signal manual override on ANY movement
                _pipeline.ForceManualOverride();

                // Mapping (Generic mappings, can be customized)
                // CC 1 (Mod Wheel) -> Width
                if (cc.Controller == MidiController.Modulation)
                {
                    float widthVal = (cc.ControllerValue / 127f) * 4.0f; // 0.0 to 4.0
                    _pipeline.Width = widthVal;
                }
                // CC 7 (Volume) -> Compression Ratio
                else if (cc.Controller == MidiController.MainVolume)
                {
                    float ratioVal = 1.0f + (cc.ControllerValue / 127f) * 19.0f; // 1.0 to 20.0
                    _pipeline.CompressionRatio = ratioVal;
                }
            }
        }

        private void OnErrorReceived(object? sender, MidiInMessageEventArgs e)
        {
            Console.WriteLine($"[MIDI] Error: {e.MidiEvent}");
        }

        public void Stop()
        {
            _midiIn?.Stop();
            _midiIn?.Dispose();
            _midiIn = null;
        }

        public void Dispose()
        {
            Stop();
        }
    }
}
