import React from 'react'
import { Layout, ConfigProvider, App } from 'antd'
import { theme } from 'antd'
import viVN from 'antd/locale/vi_VN'

const { Content } = Layout

interface AppLayoutProps {
  children: React.ReactNode
}

const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  return (
    <ConfigProvider
      locale={viVN}
      theme={{
        algorithm: theme.defaultAlgorithm,
        token: {
          // Seed Token
          colorPrimary: '#1890ff',
          borderRadius: 8,
          colorBgContainer: '#ffffff',
          
          // Alias Token
          colorBgElevated: '#ffffff',
          colorBgLayout: '#f0f8ff',
          colorBorder: '#e6f2ff',
          colorBorderSecondary: '#f0f8ff',
          
          // Typography
          fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
          fontSize: 14,
          fontSizeHeading1: 38,
          fontSizeHeading2: 30,
          fontSizeHeading3: 24,
          fontSizeHeading4: 20,
          fontSizeHeading5: 16,
          
          // Motion
          motionDurationFast: '0.1s',
          motionDurationMid: '0.2s',
          motionDurationSlow: '0.3s',
        },
        components: {
          Layout: {
            bodyBg: '#f0f8ff',
            headerBg: '#ffffff',
            siderBg: '#ffffff',
            triggerBg: '#ffffff',
            triggerColor: '#1890ff',
          },
          Menu: {
            itemBg: 'transparent',
            itemSelectedBg: '#e6f4ff',
            itemSelectedColor: '#1890ff',
            itemHoverBg: '#f0f8ff',
          },
          Card: {
            headerBg: 'transparent',
            actionsBg: '#f0f8ff',
          },
          Button: {
            borderRadius: 8,
          },
          Input: {
            borderRadius: 8,
          },
          Select: {
            borderRadius: 8,
          },
          DatePicker: {
            borderRadius: 8,
          },
          Tabs: {
            cardBg: '#fafafa',
          },
          Badge: {
            textFontSize: 12,
          },
        },
      }}
    >
      <App>
        <Layout className="app-layout">
          {children}
        </Layout>
      </App>
    </ConfigProvider>
  )
}

export default AppLayout
