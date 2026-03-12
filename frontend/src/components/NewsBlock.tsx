import { useEffect, useState } from 'react';
import { Newspaper, Calendar, Play } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';
import * as newsApi from '../api/news';
import type { NewsResponse } from '../api/types';

interface NewsBlockProps {
  limit?: number;
}

function getYouTubeId(url: string): string | null {
  const match = url.match(/(?:youtu\.be\/|youtube\.com\/(?:watch\?v=|embed\/|v\/|shorts\/))([^?&]+)/);
  return match ? match[1] : null;
}

export function NewsBlock({ limit = 5 }: NewsBlockProps) {
  const { t, language } = useLanguage();
  const [news, setNews] = useState<NewsResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedVideo, setExpandedVideo] = useState<number | null>(null);

  useEffect(() => {
    newsApi.listNews({ limit })
      .then((data) => setNews(data.news))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [limit]);

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString(language === 'kz' ? 'kk-KZ' : 'ru-RU', {
      day: 'numeric',
      month: 'long',
    });
  };

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border-2 border-gray-100 dark:border-gray-700">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-8 h-8 bg-orange-100 dark:bg-orange-900 rounded-lg flex items-center justify-center">
            <Newspaper className="w-4 h-4 text-orange-600 dark:text-orange-400" />
          </div>
          <h3 className="text-purple-700 dark:text-purple-400">{t('Новости', 'Жаңалықтар')}</h3>
        </div>
        <p className="text-gray-500 dark:text-gray-400 text-sm">{t('Загрузка...', 'Жүктелуде...')}</p>
      </div>
    );
  }

  if (news.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border-2 border-gray-100 dark:border-gray-700">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-8 h-8 bg-orange-100 dark:bg-orange-900 rounded-lg flex items-center justify-center">
            <Newspaper className="w-4 h-4 text-orange-600 dark:text-orange-400" />
          </div>
          <h3 className="text-purple-700 dark:text-purple-400">{t('Новости', 'Жаңалықтар')}</h3>
        </div>
        <p className="text-gray-500 dark:text-gray-400 text-sm">{t('Новостей пока нет', 'Жаңалықтар әлі жоқ')}</p>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border-2 border-gray-100 dark:border-gray-700">
      <div className="flex items-center gap-2 mb-4">
        <div className="w-8 h-8 bg-orange-100 dark:bg-orange-900 rounded-lg flex items-center justify-center">
          <Newspaper className="w-4 h-4 text-orange-600 dark:text-orange-400" />
        </div>
        <h3 className="text-purple-700 dark:text-purple-400">{t('Новости', 'Жаңалықтар')}</h3>
      </div>

      <div className="space-y-4">
        {news.map((item) => {
          const youtubeId = item.video_url ? getYouTubeId(item.video_url) : null;
          const isVideoExpanded = expandedVideo === item.id;

          return (
            <div key={item.id} className="border-b border-gray-100 dark:border-gray-700 last:border-0 pb-4 last:pb-0">
              {/* Image */}
              {item.image_url && (
                <div className="mb-2 rounded-lg overflow-hidden">
                  <img
                    src={item.image_url}
                    alt=""
                    className="w-full h-32 object-cover"
                    onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
                  />
                </div>
              )}

              <h4 className="text-gray-800 dark:text-gray-100 font-medium text-sm mb-1">
                {language === 'kz' && item.title_kz ? item.title_kz : item.title_ru}
              </h4>
              <p className="text-gray-600 dark:text-gray-400 text-xs mb-2 line-clamp-3">
                {language === 'kz' && item.content_kz ? item.content_kz : item.content_ru}
              </p>

              {/* Video thumbnail/player */}
              {youtubeId && (
                <div className="mb-2">
                  {isVideoExpanded ? (
                    <div className="aspect-video rounded-lg overflow-hidden">
                      <iframe
                        src={`https://www.youtube.com/embed/${youtubeId}?autoplay=1`}
                        className="w-full h-full"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowFullScreen
                      />
                    </div>
                  ) : (
                    <button
                      onClick={() => setExpandedVideo(item.id)}
                      className="relative w-full aspect-video rounded-lg overflow-hidden group"
                    >
                      <img
                        src={`https://img.youtube.com/vi/${youtubeId}/mqdefault.jpg`}
                        alt=""
                        className="w-full h-full object-cover"
                      />
                      <div className="absolute inset-0 bg-black/30 flex items-center justify-center group-hover:bg-black/40 transition-colors">
                        <div className="w-10 h-10 bg-white/90 rounded-full flex items-center justify-center">
                          <Play className="w-5 h-5 text-purple-600 ml-0.5" fill="currentColor" />
                        </div>
                      </div>
                    </button>
                  )}
                </div>
              )}

              <div className="flex items-center gap-1 text-gray-500 dark:text-gray-500 text-xs">
                <Calendar className="w-3 h-3" />
                <span>{formatDate(item.created_at)}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
