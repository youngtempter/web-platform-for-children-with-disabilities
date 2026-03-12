import { useEffect, useState } from 'react';
import { BarChart3, Users, BookOpen, GraduationCap, CheckCircle, UserCheck, School } from 'lucide-react';
import { Card } from './ui/card';
import { useLanguage } from '../contexts/LanguageContext';
import * as adminApi from '../api/admin';
import type { AdminStats as AdminStatsType } from '../api/types';

export function AdminStats() {
  const { t } = useLanguage();
  const [stats, setStats] = useState<AdminStatsType | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    adminApi.getAdminStats()
      .then(setStats)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const statCards = [
    {
      icon: Users,
      value: stats?.total_users ?? 0,
      labelRu: 'Всего пользователей',
      labelKz: 'Барлық пайдаланушылар',
      color: 'bg-blue-500',
      bgColor: 'from-blue-100 to-blue-200 dark:from-blue-900 dark:to-blue-800',
      borderColor: 'border-blue-300 dark:border-blue-700',
    },
    {
      icon: School,
      value: stats?.total_students ?? 0,
      labelRu: 'Учеников',
      labelKz: 'Оқушылар',
      color: 'bg-green-500',
      bgColor: 'from-green-100 to-green-200 dark:from-green-900 dark:to-green-800',
      borderColor: 'border-green-300 dark:border-green-700',
    },
    {
      icon: UserCheck,
      value: stats?.total_teachers ?? 0,
      labelRu: 'Учителей',
      labelKz: 'Мұғалімдер',
      color: 'bg-purple-500',
      bgColor: 'from-purple-100 to-purple-200 dark:from-purple-900 dark:to-purple-800',
      borderColor: 'border-purple-300 dark:border-purple-700',
    },
    {
      icon: BookOpen,
      value: stats?.total_courses ?? 0,
      labelRu: 'Курсов',
      labelKz: 'Курстар',
      color: 'bg-orange-500',
      bgColor: 'from-orange-100 to-orange-200 dark:from-orange-900 dark:to-orange-800',
      borderColor: 'border-orange-300 dark:border-orange-700',
    },
    {
      icon: GraduationCap,
      value: stats?.total_lessons ?? 0,
      labelRu: 'Уроков',
      labelKz: 'Сабақтар',
      color: 'bg-yellow-500',
      bgColor: 'from-yellow-100 to-yellow-200 dark:from-yellow-900 dark:to-yellow-800',
      borderColor: 'border-yellow-300 dark:border-yellow-700',
    },
    {
      icon: CheckCircle,
      value: stats?.total_enrollments ?? 0,
      labelRu: 'Записей на курсы',
      labelKz: 'Курстарға жазылулар',
      color: 'bg-red-500',
      bgColor: 'from-red-100 to-red-200 dark:from-red-900 dark:to-red-800',
      borderColor: 'border-red-300 dark:border-red-700',
    },
  ];

  const completionRate = stats && stats.total_lessons > 0
    ? Math.round((stats.completed_lessons / stats.total_lessons) * 100)
    : 0;

  return (
    <section className="container mx-auto px-4 py-8">
      <div className="flex items-center gap-2 mb-5">
        <div className="w-10 h-10 bg-purple-100 dark:bg-purple-900 rounded-xl flex items-center justify-center">
          <BarChart3 className="w-5 h-5 text-purple-600 dark:text-purple-400" />
        </div>
        <div>
          <h2 className="text-purple-700 dark:text-purple-400 text-lg">{t('Статистика платформы', 'Платформа статистикасы')}</h2>
          <p className="text-gray-600 dark:text-gray-400 text-xs">{t('Реальные данные платформы', 'Платформаның нақты деректері')}</p>
        </div>
      </div>

      {loading ? (
        <p className="text-purple-600 dark:text-purple-400 text-sm">{t('Загрузка статистики...', 'Статистика жүктелуде...')}</p>
      ) : (
        <>
          <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-3 gap-2 sm:gap-4 mb-6">
            {statCards.map((card, i) => {
              const Icon = card.icon;
              return (
                <Card
                  key={i}
                  className={`p-3 sm:p-4 bg-gradient-to-br ${card.bgColor} rounded-xl border-2 ${card.borderColor}`}
                >
                  <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-3">
                    <div className={`w-8 h-8 sm:w-10 sm:h-10 ${card.color} rounded-lg flex items-center justify-center shrink-0`}>
                      <Icon className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
                    </div>
                    <div>
                      <p className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-gray-100">{card.value}</p>
                      <p className="text-[10px] sm:text-xs text-gray-600 dark:text-gray-400 leading-tight">{t(card.labelRu, card.labelKz)}</p>
                    </div>
                  </div>
                </Card>
              );
            })}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 sm:gap-4">
            <Card className="p-3 sm:p-4 bg-white dark:bg-gray-800 rounded-xl border-2 border-gray-100 dark:border-gray-700">
              <h3 className="text-gray-800 dark:text-gray-100 text-sm font-medium mb-3">{t('Активность обучения', 'Оқу белсенділігі')}</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center gap-2">
                  <span className="text-xs sm:text-sm text-gray-600 dark:text-gray-400">{t('Уроков завершено', 'Аяқталған сабақтар')}</span>
                  <span className="text-base sm:text-lg font-semibold text-green-600 dark:text-green-400">{stats?.completed_lessons ?? 0}</span>
                </div>
                <div className="flex justify-between items-center gap-2">
                  <span className="text-xs sm:text-sm text-gray-600 dark:text-gray-400">{t('Всего уроков', 'Барлық сабақтар')}</span>
                  <span className="text-base sm:text-lg font-semibold text-gray-800 dark:text-gray-100">{stats?.total_lessons ?? 0}</span>
                </div>
                <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-green-500 rounded-full transition-all"
                    style={{ width: `${completionRate}%` }}
                  />
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {t('Процент завершения:', 'Аяқталу пайызы:')} {completionRate}%
                </p>
              </div>
            </Card>

            <Card className="p-3 sm:p-4 bg-white dark:bg-gray-800 rounded-xl border-2 border-gray-100 dark:border-gray-700">
              <h3 className="text-gray-800 dark:text-gray-100 text-sm font-medium mb-3">{t('Состав пользователей', 'Пайдаланушылар құрамы')}</h3>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full shrink-0" />
                  <span className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 flex-1">{t('Ученики', 'Оқушылар')}</span>
                  <span className="text-xs sm:text-sm font-medium text-gray-800 dark:text-gray-100">{stats?.total_students ?? 0}</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-purple-500 rounded-full shrink-0" />
                  <span className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 flex-1">{t('Учителя', 'Мұғалімдер')}</span>
                  <span className="text-xs sm:text-sm font-medium text-gray-800 dark:text-gray-100">{stats?.total_teachers ?? 0}</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-red-500 rounded-full shrink-0" />
                  <span className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 flex-1">{t('Администраторы', 'Әкімшілер')}</span>
                  <span className="text-xs sm:text-sm font-medium text-gray-800 dark:text-gray-100">{stats?.total_admins ?? 0}</span>
                </div>
              </div>
              {stats && stats.total_users > 0 && (
                <div className="flex gap-0.5 mt-3 h-2 rounded-full overflow-hidden">
                  <div className="bg-green-500" style={{ width: `${(stats.total_students / stats.total_users) * 100}%` }} />
                  <div className="bg-purple-500" style={{ width: `${(stats.total_teachers / stats.total_users) * 100}%` }} />
                  <div className="bg-red-500" style={{ width: `${(stats.total_admins / stats.total_users) * 100}%` }} />
                </div>
              )}
            </Card>
          </div>
        </>
      )}
    </section>
  );
}
