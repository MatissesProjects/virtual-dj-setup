using System;
using NAudio.Wave;

namespace VirtualDj.Engine
{
    public class WasapiCaptureService : IDisposable
    {
        private readonly WasapiLoopbackCapture _capture;
        public event EventHandler<WaveInEventArgs>? DataAvailable;

        public WasapiCaptureService()
        {
            _capture = new WasapiLoopbackCapture();
            _capture.DataAvailable += OnDataAvailable;
        }

        private void OnDataAvailable(object? sender, WaveInEventArgs e)
        {
            DataAvailable?.Invoke(this, e);
        }

        public void Start()
        {
            _capture.StartRecording();
            Console.WriteLine("Started WASAPI Loopback Capture.");
        }

        public void Stop()
        {
            _capture.StopRecording();
            Console.WriteLine("Stopped WASAPI Loopback Capture.");
        }

        public WaveFormat WaveFormat => _capture.WaveFormat;

        public void Dispose()
        {
            _capture?.Dispose();
        }
    }
}
