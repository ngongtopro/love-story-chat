import React from 'react'
import { Layout, Button, Avatar, Dropdown, Typography, Space, Badge, theme } from 'antd'
import { 
  MenuOutlined, 
  UserOutlined, 
  LogoutOutlined,
  SettingOutlined,
  BellOutlined,
} from '@ant-design/icons'
import { useAuth } from '../context/AuthContext'
import { useNavigate } from 'react-router-dom'

const { Header } = Layout
const { Text } = Typography

interface NavbarProps {
  collapsed: boolean
  setCollapsed: (collapsed: boolean) => void
}

const Navbar: React.FC<NavbarProps> = ({ collapsed, setCollapsed }) => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const { token } = theme.useToken()

  const handleMenuClick = (key: string) => {
    switch (key) {
      case 'profile':
        navigate('/profile')
        break
      case 'settings':
        navigate('/profile')
        break
      case 'logout':
        logout()
        break
    }
  }

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: 'Hồ sơ',
      onClick: () => handleMenuClick('profile'),
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: 'Cài đặt',
      onClick: () => handleMenuClick('settings'),
    },
    {
      type: 'divider' as const,
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Đăng xuất',
      onClick: () => handleMenuClick('logout'),
    },
  ]

  return (
    <Header 
      style={{ 
        position: 'fixed', 
        zIndex: 1000, 
        width: '100%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: '#fff',
        borderBottom: '1px solid #f0f0f0',
        padding: '0 24px'
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <Button
          type="text"
          icon={<MenuOutlined />}
          onClick={() => setCollapsed(!collapsed)}
          style={{ marginRight: 16 }}
        />
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <span style={{ fontSize: 24, marginRight: 8 }}>☁️</span>
          <Text strong style={{ fontSize: 18, color: token.colorPrimary }}>
            Love Chat
          </Text>
        </div>
      </div>

      <Space size="middle">
        <Badge count={5} size="small">
          <Button 
            type="text" 
            icon={<BellOutlined />} 
            size="large"
            style={{ color: token.colorTextSecondary }}
          />
        </Badge>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Text type="secondary" style={{ fontSize: 14 }}>
            Xin chào, <Text strong>{user?.username || 'User'}</Text>
          </Text>
          <Dropdown 
            menu={{ items: userMenuItems }}
            placement="bottomRight"
            arrow
            trigger={['click']}
          >
            <Avatar 
              icon={<UserOutlined />}
              style={{ 
                backgroundColor: token.colorPrimary,
                cursor: 'pointer',
                border: `2px solid ${token.colorBorder}` 
              }}
              size="default"
            />
          </Dropdown>
        </div>
      </Space>
    </Header>
  )
}

export default Navbar
