/**
 * AUTO-GENERATED staging fixture (manual for now)
 * Points to staging URLs: *.solopide.me
 *
 * Usage:
 *   import clients from './clients-staging'
 *   clients['codelpa-staging'].baseURL  // https://beta-codelpa.solopide.me
 *   clients['surtiventas-staging'].baseURL  // https://surtiventas.solopide.me
 */

import { test as base, expect } from '@playwright/test';

function creds(prefix: string) {
  return {
    email: process.env[`${prefix}_EMAIL`] || '',
    password: process.env[`${prefix}_PASSWORD`] || '',
  };
}

interface ClientConfig {
  name: string;
  baseURL: string;
  loginPath: string;
  credentials: { email: string; password: string };
  config: Record<string, any>;
  coupons?: Array<{ code: string; discount: any }>;
  banners?: Array<{ title: string; position: string }>;
  promotions?: Array<any>;
  integrations?: { segments: any; overrides: any; userSegments: any };
}

const clients: Record<string, ClientConfig> = {
  'codelpa-staging': {
    name: 'Codelpa (staging)',
    baseURL: 'https://beta-codelpa.solopide.me',
    loginPath: '/login',
    credentials: creds('CODELPA'),
    coupons: [],
    banners: [],
    promotions: [],
    integrations: { segments: [], overrides: [], userSegments: [] },
    // Conditional tests: C2-E10, C2-E4, C2-E5, C2-E9, C3-E3, C3-E4, C3-E6, C6-E3, P1-12, P2-02, +8 more
    config: {
      anonymousAccess: false,
      anonymousHideCart: true,
      anonymousHidePrice: true,
      disableCart: false,
      disableCommerceEdit: true,
      enableCoupons: true,
      enableOrderApproval: true,
      enableOrderValidation: true,
      enableSellerDiscount: true,
      editAddress: false,
      currency: 'clp',
      hideReceiptType: true,
      purchaseOrderEnabled: true,
      ordersRequireVerification: false,
      ordersRequireAuthorization: false,
      showEmptyCategories: false,
      includeTaxRateInPrices: false,
      payment: { enableNewPaymentModule: false },
      synchronization: { enableSyncImages: true },
      useMongoPricing: true,
    },
  },

  'surtiventas-staging': {
    name: 'Surtiventas (staging)',
    baseURL: 'https://surtiventas.solopide.me',
    loginPath: '/auth/jwt/login',
    credentials: creds('SURTIVENTAS'),
    coupons: [],
    banners: [],
    promotions: [],
    integrations: { segments: [], overrides: [], userSegments: [] },
    // Conditional tests: C2-E9, P1-03, P2-03, P3-01, P3-02, V1-E4
    config: {
      anonymousAccess: false,
      anonymousHideCart: false,
      anonymousHidePrice: false,
      currency: 'clp',
      enableCoupons: true,
      enableOrderApproval: false,
      editAddress: true,
      hideReceiptType: false,
      ordersRequireAuthorization: false,
      ordersRequireVerification: false,
      payment: { enableNewPaymentModule: true },
      synchronization: { enableSyncImages: true },
    },
  },
};

export default clients;
