import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';

type Section = {
  heading: string;
  body: string;
};

type PrivacyCopy = {
  title: string;
  subtitle: string;
  updatedAt: string;
  backHome: string;
  sections: Section[];
};

const COPY: Record<'zh-CN' | 'en-US', PrivacyCopy> = {
  'zh-CN': {
    title: '隐私政策',
    subtitle: '我们如何收集、使用与保护你的信息',
    updatedAt: '最后更新：2026-02-20',
    backHome: '返回首页',
    sections: [
      {
        heading: '1. 收集的信息',
        body: '我们会收集你提供的账号信息、量表答案、对话内容与功能使用记录，仅用于提供产品功能与安全分流。',
      },
      {
        heading: '2. 信息使用目的',
        body: '你的数据用于账号管理、心理量表评估、风险检测、功能授权和服务改进，不用于未经同意的广告投放。',
      },
      {
        heading: '3. 数据安全与保存',
        body: '我们采用加密传输与存储机制，限制内部访问权限，并按合规要求进行数据保留与删除。',
      },
      {
        heading: '4. 你的权利',
        body: '你可请求导出或删除个人数据。请注意：本产品为心理教练工具，不提供医疗诊断与处方建议。',
      },
    ],
  },
  'en-US': {
    title: 'Privacy Policy',
    subtitle: 'How we collect, use, and protect your information',
    updatedAt: 'Last updated: 2026-02-20',
    backHome: 'Back to home',
    sections: [
      {
        heading: '1. Information We Collect',
        body: 'We collect account details, assessment responses, conversation data, and usage logs that you provide for service delivery and safety triage.',
      },
      {
        heading: '2. How We Use Information',
        body: 'Your data is used for account management, assessment scoring, risk detection, entitlement control, and service improvement.',
      },
      {
        heading: '3. Data Security and Retention',
        body: 'We apply encrypted transport and storage, strict internal access controls, and retention/deletion practices aligned with compliance requirements.',
      },
      {
        heading: '4. Your Rights',
        body: 'You may request data export or deletion. This product is a mental wellness coaching tool and does not provide medical diagnosis or prescriptions.',
      },
    ],
  },
};

export default function PrivacyPage() {
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
            {copy.backHome}
          </Link>
        </div>
      </motion.div>
    </div>
  );
}
