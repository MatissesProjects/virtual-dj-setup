using System;
using System.Net.Sockets;
using System.Threading;
using System.Collections.Concurrent;

namespace VirtualDj.Engine
{
    /// <summary>
    /// Extends the audio bridge to support remote AI processing over the local network.
    /// Uses raw TCP sockets for high-bandwidth PCM streaming.
    /// </summary>
    public class NetworkAudioBridge : IDisposable
    {
        private readonly string _remoteIp;
        private readonly int _port;
        private TcpClient _client;
        private NetworkStream _stream;
        private bool _isConnected;
        
        private const int BlockSize = 1024;
        private const int Channels = 2;
        private const int FloatSize = 4;
        private const int PayloadSize = BlockSize * Channels * FloatSize;

        // Buffers for incoming stems
        private readonly ConcurrentDictionary<int, float[]> _stemBuffers = new ConcurrentDictionary<int, float[]>();

        public NetworkAudioBridge(string remoteIp = "127.0.0.1", int port = 7777)
        {
            _remoteIp = remoteIp;
            _port = port;
            
            // Initialize stem buffers (1=Vocals, 2=Drums, 3=Bass, 4=Other, 5=Bridge)
            for (int i = 1; i <= 5; i++)
                _stemBuffers[i] = new float[BlockSize * Channels];
        }

        public void Connect()
        {
            try
            {
                _client = new TcpClient(_remoteIp, _port);
                _stream = _client.GetStream();
                _isConnected = true;
                
                // Start a background thread to read processed stems back
                new Thread(ReadLoop) { IsBackground = true }.Start();
                Console.WriteLine($"[NETWORK] Connected to AI Node at {_remoteIp}:{_port}");
            }
            catch (Exception e)
            {
                Console.WriteLine($"[NETWORK] Connection failed: {e.Message}");
                _isConnected = false;
            }
        }

        public void SendInput(float[] samples, int count)
        {
            if (!_isConnected) return;

            try
            {
                // Simple protocol: [4 bytes count] [Raw PCM Bytes]
                byte[] header = BitConverter.GetBytes(count * FloatSize);
                byte[] data = new byte[count * FloatSize];
                Buffer.BlockCopy(samples, 0, data, 0, data.Length);
                
                _stream.Write(header, 0, 4);
                _stream.Write(data, 0, data.Length);
            }
            catch
            {
                _isConnected = false;
            }
        }

        private void ReadLoop()
        {
            byte[] header = new byte[4];
            while (_isConnected)
            {
                try
                {
                    // Expecting: [4 bytes stemIndex] [4 bytes dataSize] [Raw PCM Bytes]
                    if (_stream.Read(header, 0, 4) == 4)
                    {
                        int stemIndex = BitConverter.ToInt32(header, 0);
                        _stream.Read(header, 0, 4);
                        int dataSize = BitConverter.ToInt32(header, 0);
                        
                        byte[] data = new byte[dataSize];
                        int read = 0;
                        while (read < dataSize)
                        {
                            read += _stream.Read(data, read, dataSize - read);
                        }

                        if (_stemBuffers.TryGetValue(stemIndex, out float[] buffer))
                        {
                            Buffer.BlockCopy(data, 0, buffer, 0, dataSize);
                        }
                    }
                }
                catch
                {
                    _isConnected = false;
                }
            }
        }

        public float[] GetStem(int stemIndex)
        {
            return _stemBuffers.TryGetValue(stemIndex, out float[] buffer) ? buffer : new float[0];
        }

        public bool IsConnected => _isConnected;

        public void Dispose()
        {
            _isConnected = false;
            _stream?.Dispose();
            _client?.Dispose();
        }
    }
}
