import React from 'react'
import { Layout, Menu, Badge, theme } from 'antd'
import { useNavigate, useLocation } from 'react-router-dom'
import type { MenuProps } from 'antd'
import { 
  HomeOutlined,
  MessageOutlined,
  UserOutlined,
  PlayCircleOutlined,
  BugOutlined,
  WalletOutlined,
  TrophyOutlined,
  ShopOutlined
} from '@ant-design/icons'

const { Sider } = Layout

interface SidebarProps {
  collapsed: boolean
}

type MenuItem = Required<MenuProps>['items'][number]

const Sidebar: React.FC<SidebarProps> = ({ collapsed }) => {
  const navigate = useNavigate()
  const location = useLocation()
  const { token } = theme.useToken()

  const menuItems: MenuProps['items'] = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: 'Trang chủ',
    },
    {
      key: '/chat',
      icon: (
        <Badge count={3} size="small" offset={[4, 0]}>
          <MessageOutlined />
        </Badge>
      ),
      label: 'Tin nhắn',
    },
    {
      key: '/profile',
      icon: <UserOutlined />,
      label: 'Hồ sơ',
    },
    {
      key: 'games',
      icon: <PlayCircleOutlined />,
      label: 'Trò chơi',
      children: [
        {
          key: '/caro',
          icon: <TrophyOutlined />,
          label: 'Caro Online',
        },
      ],
    },
    {
      key: '/farm',
      icon: <BugOutlined />,
      label: 'Trang trại',
    },
    {
      key: '/wallet',
      icon: <WalletOutlined />,
      label: 'Ví tiền',
    },
  ]

  const handleMenuClick: MenuProps['onClick'] = ({ key }) => {
    navigate(key as string)
  }

  return (
    <Sider
      trigger={null}
      collapsible
      collapsed={collapsed}
      style={{
        position: 'fixed',
        left: 0,
        top: 64,
        bottom: 0,
        zIndex: 100,
        background: '#fff',
        borderRight: '1px solid #f0f0f0',
      }}
    >
      <Menu
        mode="inline"
        selectedKeys={[location.pathname]}
        items={menuItems}
        onClick={handleMenuClick}
        style={{
          height: '100%',
          borderRight: 0,
        }}
      />
    </Sider>
  )
}

export default Sidebar
