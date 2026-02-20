import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../stores/auth';
import Card from '../../components/Card/Card';
import Button from '../../components/Button/Button';

export default function ProfilePage() {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const { userId, email, channel, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div className="max-w-lg mx-auto">
      <h1 className="font-heading text-3xl font-bold mb-8">{t('nav.profile')}</h1>

      <Card className="mb-6">
        <h3 className="font-heading font-bold mb-4">{t('auth.email')}</h3>
        <p className="text-muted">{email ?? '-'}</p>
        <p className="text-xs text-muted mt-2">ID: {userId ?? '-'}</p>
        {channel && (
          <div className="mt-3 flex items-center gap-2">
            <span className="text-sm text-muted">通道:</span>
            <span className={`text-sm font-semibold ${
              channel === 'GREEN' ? 'text-safe' : channel === 'YELLOW' ? 'text-warn' : 'text-danger'
            }`}>
              {channel}
            </span>
          </div>
        )}
      </Card>

      <Card className="mb-6">
        <h3 className="font-heading font-bold mb-4">语言 / Language</h3>
        <div className="flex gap-3">
          <Button
            variant={i18n.language === 'zh-CN' ? 'primary' : 'ghost'}
            size="sm"
            onClick={() => i18n.changeLanguage('zh-CN')}
          >
            中文
          </Button>
          <Button
            variant={i18n.language === 'en-US' ? 'primary' : 'ghost'}
            size="sm"
            onClick={() => i18n.changeLanguage('en-US')}
          >
            English
          </Button>
        </div>
      </Card>

      <Card className="mb-6">
        <h3 className="font-heading font-bold mb-4">{t('safety.title')}</h3>
        <Button variant="ghost" size="sm" onClick={() => navigate('/safety')}>
          {t('safety.subtitle')} →
        </Button>
      </Card>

      <Button variant="danger" className="w-full" onClick={handleLogout}>
        {i18n.language === 'zh-CN' ? '退出登录' : 'Log Out'}
      </Button>
    </div>
  );
}
