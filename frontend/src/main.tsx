import React from 'react'
import ReactDOM from 'react-dom/client'
import { ConfigProvider } from 'antd'
import viVN from 'antd/locale/vi_VN'
import dayjs from 'dayjs'
import 'dayjs/locale/vi'
import App from './App'
import './index.css'

// Set dayjs locale to Vietnamese
dayjs.locale('vi')

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ConfigProvider 
      locale={viVN}
      theme={{
        token: {
          colorPrimary: '#ff69b4',
          borderRadius: 8,
          colorBgContainer: '#ffffff',
        },
        components: {
          Layout: {
            bodyBg: '#f5f5f5',
            headerBg: '#ffffff',
            siderBg: '#ffffff',
          },
        },
      }}
    >
      <App />
    </ConfigProvider>
  </React.StrictMode>,
)
