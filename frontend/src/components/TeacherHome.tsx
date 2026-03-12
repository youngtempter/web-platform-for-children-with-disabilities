import { useEffect, useState } from 'react';
import { Home, BookOpen, Users, TrendingUp, ArrowRight } from 'lucide-react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { useLanguage } from '../contexts/LanguageContext';
import { useAuth } from '../contexts/AuthContext';
import { NewsBlock } from './NewsBlock';
import * as teacherApi from '../api/teacher';
import type { TeacherStats } from '../api/types';

interface TeacherHomeProps {
  setActiveSection: (section: string) => void;
}

export function TeacherHome({ setActiveSection }: TeacherHomeProps) {
  const { t } = useLanguage();
  const { user } = useAuth();
  const [stats, setStats] = useState<TeacherStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    teacherApi.getTeacherStats()
      .then(setStats)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const statItems = [
    { 
      icon: BookOpen, 
      value: stats?.total_courses ?? 0, 
      labelRu: 'Мои курсы', 
      labelKz: 'Менің курстарым',
      color: 'bg-blue-500',
      bgLight: 'bg-blue-100 dark:bg-blue-900/50',
    },
    { 
      icon: Users, 
      value: stats?.total_students ?? 0, 
      labelRu: 'Учеников', 
      labelKz: 'Оқушылар',
      color: 'bg-green-500',
      bgLight: 'bg-green-100 dark:bg-green-900/50',
    },
    { 
      icon: TrendingUp, 
      value: `${stats?.average_progress?.toFixed(0) ?? 0}%`, 
      labelRu: 'Средний прогресс', 
      labelKz: 'Орташа үлгерім',
      color: 'bg-purple-500',
      bgLight: 'bg-purple-100 dark:bg-purple-900/50',
    },
  ];

  return (
    <section className="container mx-auto px-4 py-8">
      {/* Header with welcome */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 bg-purple-100 dark:bg-purple-900 rounded-xl flex items-center justify-center">
            <Home className="w-5 h-5 text-purple-600 dark:text-purple-400" />
          </div>
          <div>
            <h2 className="text-purple-700 dark:text-purple-400 text-lg">
              {t('Добро пожаловать', 'Қош келдіңіз')}, {user?.first_name || t('Учитель', 'Мұғалім')}!
            </h2>
            <p className="text-gray-600 dark:text-gray-400 text-xs">
              {t('Ваша главная страница', 'Сіздің басты бетіңіз')}
            </p>
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        {/* Left column - Stats and Quick Actions */}
        <div className="md:col-span-2 space-y-6">
          {/* Stats */}
          {loading ? (
            <p className="text-purple-600 dark:text-purple-400 text-sm">{t('Загрузка...', 'Жүктелуде...')}</p>
          ) : (
            <div className="grid sm:grid-cols-3 gap-4">
              {statItems.map((item, i) => {
                const Icon = item.icon;
                return (
                  <Card key={i} className="p-4 bg-white dark:bg-gray-800 rounded-xl border-2 border-gray-100 dark:border-gray-700">
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 ${item.bgLight} rounded-xl flex items-center justify-center shrink-0`}>
                        <Icon className={`w-5 h-5 ${item.color.replace('bg-', 'text-').replace('-500', '-600')}`} />
                      </div>
                      <div>
                        <p className="text-2xl font-semibold text-gray-900 dark:text-gray-100 leading-tight">{item.value}</p>
                        <p className="text-xs text-gray-600 dark:text-gray-400">{t(item.labelRu, item.labelKz)}</p>
                      </div>
                    </div>
                  </Card>
                );
              })}
            </div>
          )}

          {/* Quick Actions */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border-2 border-gray-100 dark:border-gray-700">
            <h3 className="text-gray-800 dark:text-gray-100 font-medium mb-4">{t('Быстрые действия', 'Жылдам әрекеттер')}</h3>
            <div className="grid sm:grid-cols-2 gap-3">
              <Button
                variant="outline"
                className="justify-between h-auto py-3 px-4 rounded-xl border-2 border-gray-200 dark:border-gray-600 dark:hover:bg-gray-700"
                onClick={() => setActiveSection('courses')}
              >
                <span className="flex items-center gap-2">
                  <BookOpen className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                  <span className="text-gray-700 dark:text-gray-300">{t('Мои курсы', 'Менің курстарым')}</span>
                </span>
                <ArrowRight className="w-4 h-4 text-gray-400" />
              </Button>
              <Button
                variant="outline"
                className="justify-between h-auto py-3 px-4 rounded-xl border-2 border-gray-200 dark:border-gray-600 dark:hover:bg-gray-700"
                onClick={() => setActiveSection('students')}
              >
                <span className="flex items-center gap-2">
                  <Users className="w-4 h-4 text-green-600 dark:text-green-400" />
                  <span className="text-gray-700 dark:text-gray-300">{t('Мои ученики', 'Менің оқушыларым')}</span>
                </span>
                <ArrowRight className="w-4 h-4 text-gray-400" />
              </Button>
            </div>
          </div>
        </div>

        {/* Right column - News */}
        <div>
          <NewsBlock limit={5} />
        </div>
      </div>
    </section>
  );
}
