import { useState, ReactNode } from 'react'
import { Layout } from 'antd'
import Navbar from '../components/Navbar'
import Sidebar from '../components/Sidebar'

const { Content } = Layout

interface AppLayoutProps {
  children: ReactNode
}

export default function AppLayout({ children }: AppLayoutProps) {
  const [collapsed, setCollapsed] = useState(false)

  return (
    <Layout className="full-height">
      <Navbar collapsed={collapsed} setCollapsed={setCollapsed} />
      <Layout>
        <Sidebar collapsed={collapsed} />
        <Layout style={{ marginLeft: collapsed ? 80 : 200 }}>
          <Content style={{ margin: '16px', overflow: 'auto' }}>
            {children}
          </Content>
        </Layout>
      </Layout>
    </Layout>
  )
}
