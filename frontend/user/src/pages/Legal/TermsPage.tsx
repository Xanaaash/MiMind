import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';

type Section = {
  heading: string;
  body: string;
};

type TermsCopy = {
  title: string;
  subtitle: string;
  updatedAt: string;
  sections: Section[];
};

const COPY: Record<'zh-CN' | 'en-US', TermsCopy> = {
  'zh-CN': {
    title: '服务条款',
    subtitle: '使用 MindCoach AI 前请阅读以下条款',
    updatedAt: '最后更新：2026-02-20',
    sections: [
      {
        heading: '1. 服务性质',
        body: 'MindCoach AI 是心理教练平台，不属于医疗服务，不提供临床诊断、治疗或药物建议。',
      },
      {
        heading: '2. 用户责任',
        body: '你应提供真实信息并合理使用产品，不得用于违法违规用途，不得绕过平台安全机制。',
      },
      {
        heading: '3. 风险与求助',
        body: '若出现自伤/伤他或其他紧急风险，请立即联系当地紧急服务或专业机构，平台会触发安全引导机制。',
      },
      {
        heading: '4. 条款调整',
        body: '我们可能根据产品迭代和合规要求更新条款。继续使用服务即表示你接受更新后的版本。',
      },
    ],
  },
  'en-US': {
    title: 'Terms of Service',
    subtitle: 'Please review these terms before using MindCoach AI',
    updatedAt: 'Last updated: 2026-02-20',
    sections: [
      {
        heading: '1. Nature of Service',
        body: 'MindCoach AI is a mental wellness coaching platform, not a medical service, and does not provide diagnosis, treatment, or medication advice.',
      },
      {
        heading: '2. User Responsibilities',
        body: 'You agree to provide accurate information, use the platform lawfully, and not bypass safety protections.',
      },
      {
        heading: '3. Risk and Emergency Support',
        body: 'If there is self-harm, harm-to-others, or any immediate danger, contact local emergency or professional services immediately.',
      },
      {
        heading: '4. Updates to Terms',
        body: 'We may update these terms for product and compliance reasons. Continued use indicates acceptance of the latest version.',
      },
    ],
  },
};

export default function TermsPage() {
  const { i18n } = useTranslation();
  const lang = i18n.language === 'en-US' ? 'en-US' : 'zh-CN';
  const copy = COPY[lang];

  return (
    <div className="min-h-screen px-4 py-12">
      <motion.div
        className="max-w-3xl mx-auto bg-panel border border-line rounded-3xl p-8 shadow-sm"
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="mb-6">
          <h1 className="font-heading text-3xl font-bold">{copy.title}</h1>
          <p className="text-muted mt-1">{copy.subtitle}</p>
          <p className="text-xs text-muted mt-2">{copy.updatedAt}</p>
        </div>

        <div className="space-y-5">
          {copy.sections.map((section) => (
            <section key={section.heading}>
              <h2 className="font-heading font-bold text-lg">{section.heading}</h2>
              <p className="text-muted text-sm mt-1 leading-relaxed">{section.body}</p>
            </section>
          ))}
        </div>

        <div className="mt-8">
          <Link to="/" className="text-sm font-semibold text-accent hover:underline">
            {lang === 'zh-CN' ? '返回首页' : 'Back to home'}
          </Link>
        </div>
      </motion.div>
    </div>
  );
}
