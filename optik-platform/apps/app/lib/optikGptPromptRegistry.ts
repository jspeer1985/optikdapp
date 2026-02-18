export type OptikPromptProfile = {
  id: string;
  label: string;
  version: string;
  description: string;
};

export const OPTIK_PROMPT_PROFILES: Record<string, OptikPromptProfile> = {
  'optik-master': {
    id: 'optik-master',
    label: 'Optik Enterprise Master',
    version: '2024-02-16',
    description: 'Enterprise commerce copilot with proof-of-completion gates.'
  },
  'claude-master': {
    id: 'claude-master',
    label: 'Claude Master Style',
    version: '2024-02-16',
    description: 'Careful, structured, and validation-first responses.'
  },
  'openai-master': {
    id: 'openai-master',
    label: 'OpenAI Master Style',
    version: '2024-02-16',
    description: 'Direct, action-led, and execution focused.'
  },
  'shopify-assistant': {
    id: 'shopify-assistant',
    label: 'Shopify Commerce Assistant',
    version: '2024-02-16',
    description: 'Catalog, pricing, payments, and growth operations.'
  }
};

export const OPTIK_DEFAULT_PROMPT = OPTIK_PROMPT_PROFILES['optik-master'];
