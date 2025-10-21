import React, { useState, useEffect } from 'react'
import { 
  Row, 
  Col, 
  Card, 
  Statistic, 
  List, 
  Avatar, 
  Button,
  Typography,
  Space,
  Badge,
  Spin
} from 'antd'
import { 
  MessageOutlined,
  PlayCircleOutlined,
  BugOutlined,
  WalletOutlined,
  UserOutlined,
  TrophyOutlined
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { chatAPI, caroAPI, farmAPI, walletAPI } from '../services/api'

const { Title, Text } = Typography

// Types
interface User {
  id: number
  username: string
  is_online?: boolean
}

interface Message {
  id: number
  content: string
  created_at: string
}

interface Chat {
  id: number
  other_user?: User
  latest_message?: Message
  unread_count: number
}

interface GameStats {
  games_won?: number
  games_played?: number
  win_rate?: number
}

interface FarmStats {
  level?: number
  coins?: number
  plants?: number
}

interface WalletStats {
  current_balance?: number
  total_transactions?: number
}

interface HomeData {
  recentChats: Chat[]
  gameStats: GameStats
  farmStats: FarmStats
  walletStats: WalletStats
  onlineUsers: User[]
}

const Home: React.FC = () => {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState<HomeData>({
    recentChats: [],
    gameStats: {},
    farmStats: {},
    walletStats: {},
    onlineUsers: []
  })

  useEffect(() => {
    loadHomeData()
  }, [])

  const loadHomeData = async () => {
    try {
      setLoading(true)
      
      // Load data from multiple APIs
      const [chatsRes, usersRes] = await Promise.all([
        chatAPI.getPrivateChats().catch(() => ({ data: [] })),
        chatAPI.getUsers().catch(() => ({ data: [] }))
      ])

      // Try to load game, farm, and wallet stats (may fail if not implemented)
      let gameStats = {}
      let farmStats = {}
      let walletStats = {}

      try {
        const gameRes = await caroAPI.getStats()
        gameStats = gameRes.data
      } catch (error) {
        console.log('Game stats not available')
      }

      try {
        const farmRes = await farmAPI.getStats()
        farmStats = farmRes.data
      } catch (error) {
        console.log('Farm stats not available')
      }

      try {
        const walletRes = await walletAPI.getStats()
        walletStats = walletRes.data
      } catch (error) {
        console.log('Wallet stats not available')
      }

      setData({
        recentChats: chatsRes.data.slice(0, 5),
        gameStats,
        farmStats,
        walletStats,
        onlineUsers: usersRes.data.filter((user: User) => user.is_online).slice(0, 10)
      })
    } catch (error) {
      console.error('Error loading home data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '50vh' 
      }}>
        <Spin size="large" />
      </div>
    )
  }

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>
          <Space>
            <span>💕</span>
            Chào mừng đến với Love Chat!
          </Space>
        </Title>
        <Text type="secondary">
          Kết nối, trò chuyện và vui chơi cùng bạn bè
        </Text>
      </div>

      {/* Statistics Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Tin nhắn"
              value={data.recentChats.length}
              prefix={<MessageOutlined style={{ color: '#1890ff' }} />}
            />
            <Button 
              type="link" 
              onClick={() => navigate('/chat')}
              style={{ padding: 0, marginTop: 8 }}
            >
              Xem tất cả
            </Button>
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Trận thắng"
              value={data.gameStats.games_won || 0}
              prefix={<TrophyOutlined style={{ color: '#52c41a' }} />}
            />
            <Button 
              type="link" 
              onClick={() => navigate('/caro')}
              style={{ padding: 0, marginTop: 8 }}
            >
              Chơi game
            </Button>
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Cấp độ trang trại"
              value={data.farmStats.level || 1}
              prefix={<BugOutlined style={{ color: '#fa8c16' }} />}
            />
            <Button 
              type="link" 
              onClick={() => navigate('/farm')}
              style={{ padding: 0, marginTop: 8 }}
            >
              Vào trang trại
            </Button>
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Số dư ví"
              value={data.walletStats.current_balance || 0}
              prefix={<WalletOutlined style={{ color: '#eb2f96' }} />}
              suffix="đ"
            />
            <Button 
              type="link" 
              onClick={() => navigate('/wallet')}
              style={{ padding: 0, marginTop: 8 }}
            >
              Quản lý ví
            </Button>
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        {/* Recent Chats */}
        <Col xs={24} lg={12}>
          <Card 
            title="Tin nhắn gần đây" 
            extra={
              <Button type="link" onClick={() => navigate('/chat')}>
                Xem tất cả
              </Button>
            }
          >
            <List
              dataSource={data.recentChats}
              renderItem={(chat) => (
                <List.Item
                  onClick={() => navigate(`/chat/${chat.other_user?.id}`)}
                  style={{ cursor: 'pointer' }}
                >
                  <List.Item.Meta
                    avatar={
                      <Badge dot={chat.unread_count > 0} status="processing">
                        <Avatar icon={<UserOutlined />} />
                      </Badge>
                    }
                    title={chat.other_user?.username || 'Người dùng'}
                    description={
                      chat.latest_message ? 
                        `${chat.latest_message.content.slice(0, 50)}...` : 
                        'Chưa có tin nhắn'
                    }
                  />
                  {chat.unread_count > 0 && (
                    <Badge count={chat.unread_count} />
                  )}
                </List.Item>
              )}
              locale={{ emptyText: 'Chưa có cuộc trò chuyện nào' }}
            />
          </Card>
        </Col>

        {/* Online Users */}
        <Col xs={24} lg={12}>
          <Card title="Người dùng đang online">
            <List
              dataSource={data.onlineUsers}
              renderItem={(user) => (
                <List.Item
                  onClick={() => navigate(`/chat/${user.id}`)}
                  style={{ cursor: 'pointer' }}
                >
                  <List.Item.Meta
                    avatar={
                      <Badge dot status="success">
                        <Avatar icon={<UserOutlined />} />
                      </Badge>
                    }
                    title={user.username}
                    description="Đang online"
                  />
                  <Button 
                    type="primary" 
                    size="small"
                    icon={<MessageOutlined />}
                  >
                    Nhắn tin
                  </Button>
                </List.Item>
              )}
              locale={{ emptyText: 'Không có ai online' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Quick Actions */}
      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col span={24}>
          <Card title="Hành động nhanh">
            <Space wrap>
              <Button 
                type="primary" 
                icon={<MessageOutlined />}
                onClick={() => navigate('/chat')}
              >
                Bắt đầu trò chuyện
              </Button>
              <Button 
                icon={<PlayCircleOutlined />}
                onClick={() => navigate('/caro')}
              >
                Chơi game Caro
              </Button>
              <Button 
                icon={<BugOutlined />}
                onClick={() => navigate('/farm')}
              >
                Chăm sóc trang trại
              </Button>
              <Button 
                icon={<WalletOutlined />}
                onClick={() => navigate('/wallet')}
              >
                Kiểm tra ví tiền
              </Button>
            </Space>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Home
