using System.Collections.Generic;

namespace VirtualDj.Engine
{
    public class Song
    {
        public string Title { get; set; } = "";
        public string Artist { get; set; } = "";
        public string Id => $"{Artist} - {Title}";
    }

    public class PlaylistManager
    {
        private readonly List<Song> _playlist = new List<Song>();
        private int _currentIndex = -1;

        public void AddSong(string title, string artist)
        {
            _playlist.Add(new Song { Title = title, Artist = artist });
            if (_currentIndex == -1) _currentIndex = 0;
        }

        public Song? CurrentSong => (_currentIndex >= 0 && _currentIndex < _playlist.Count) ? _playlist[_currentIndex] : null;

        public void Next()
        {
            if (_currentIndex < _playlist.Count - 1)
                _currentIndex++;
        }

        public List<Song> GetPlaylist() => _playlist;
    }
}
