import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Row,
  Col,
  Card,
  List,
  Avatar,
  Input,
  Button,
  Typography,
  Space,
  Badge,
  Spin,
  App,
  Empty
} from 'antd'
import {
  SendOutlined,
  UserOutlined,
  MessageOutlined
} from '@ant-design/icons'
import { chatAPI } from '../../services/api'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import '../../styles/Chat.css'

// Add relativeTime plugin for dayjs
dayjs.extend(relativeTime)

// Interfaces
interface User {
  id: number
  username: string
  email: string
  is_online?: boolean
  first_name?: string
  last_name?: string
}

interface Message {
  id: number
  content: string
  timestamp: string
  sender: User
  is_own_message?: boolean
}

interface PrivateChat {
  id: number
  participants: User[]
  created_at: string
}

const { TextArea } = Input
const { Text } = Typography

export default function ChatPage() {
  const { userId } = useParams()
  const navigate = useNavigate()
  const { message } = App.useApp()
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [messageText, setMessageText] = useState('')
  const [users, setUsers] = useState<User[]>([])
  const [messages, setMessages] = useState<Message[]>([])
  const [currentChat, setCurrentChat] = useState<PrivateChat | null>(null)
  const [selectedUser, setSelectedUser] = useState<User | null>(null)

  useEffect(() => {
    loadUsers()
  }, [])

  useEffect(() => {
    if (userId) {
      selectUser(userId)
    }
  }, [userId])

  const loadUsers = async () => {
    try {
      const response = await chatAPI.getUsers()
      console.log('Users API Response:', response.data)
      setUsers(Array.isArray(response.data) ? response.data : [])
    } catch (error) {
      console.error('Error loading users:', error)
      message.error('Không thể tải danh sách người dùng')
    } finally {
      setLoading(false)
    }
  }

  const selectUser = async (selectedUserId: string | number) => {
    try {
      setLoading(true)
      const numericUserId = typeof selectedUserId === 'string' ? parseInt(selectedUserId) : selectedUserId
      const user = users.find(u => u.id === numericUserId)
      if (!user) {
        // If users not loaded yet, try to load them first
        await loadUsers()
        const foundUser = users.find(u => u.id === numericUserId)
        if (!foundUser) {
          message.error('Không tìm thấy người dùng')
          return
        }
        setSelectedUser(foundUser)
      } else {
        setSelectedUser(user)
      }

      // Create or get existing chat
      const chatResponse = await chatAPI.createPrivateChat(numericUserId)
      console.log('Chat API Response:', chatResponse.data)
      setCurrentChat(chatResponse.data)

      // Load messages for this chat
      const messagesResponse = await chatAPI.getMessages(chatResponse.data.id)
      console.log('Messages API Response:', messagesResponse.data)
      setMessages(Array.isArray(messagesResponse.data) ? messagesResponse.data : [])
      
      navigate(`/chat/${selectedUserId}`)
    } catch (error) {
      console.error('Error selecting user:', error)
      message.error('Không thể tải cuộc trò chuyện')
    } finally {
      setLoading(false)
    }
  }

  const sendMessage = async () => {
    if (!messageText.trim() || !currentChat) return

    try {
      setSending(true)
      const response = await chatAPI.sendMessage(currentChat.id, messageText.trim())
      
      // Add new message to the list (ensure response.data exists)
      if (response.data) {
        setMessages(prev => Array.isArray(prev) ? [...prev, response.data] : [response.data])
      }
      setMessageText('')
    } catch (error) {
      console.error('Error sending message:', error)
      message.error('Không thể gửi tin nhắn')
    } finally {
      setSending(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '50vh',
        flexDirection: 'column'
      }}>
        <Spin size="large" />
        <Text style={{ marginTop: 16, color: '#1890ff' }}>
          Đang tải danh sách người dùng...
        </Text>
      </div>
    )
  }

  return (
    <Row gutter={16} className="chat-container">
      {/* Users List */}
      <Col xs={24} md={8}>
        <Card 
          title="Danh sách người dùng" 
          style={{ height: '100%' }}
          styles={{ body: { padding: 0, height: 'calc(100% - 57px)', overflow: 'auto' } }}
        >
          <List
            dataSource={Array.isArray(users) ? users : []}
            renderItem={(user) => (
              <List.Item
                onClick={() => selectUser(user.id)}
                className={`chat-user-item ${selectedUser?.id === user.id ? 'selected' : ''}`}
              >
                <List.Item.Meta
                  avatar={
                    <Badge dot={user.is_online} status={user.is_online ? 'success' : 'default'}>
                      <Avatar icon={<UserOutlined />} />
                    </Badge>
                  }
                  title={user.username}
                  description={user.is_online ? 'Đang online' : 'Offline'}
                />
              </List.Item>
            )}
          />
        </Card>
      </Col>

      {/* Chat Area */}
      <Col xs={24} md={16}>
        <Card 
          title={
            selectedUser ? (
              <Space>
                <Avatar icon={<UserOutlined />} />
                <span>{selectedUser.username}</span>
                <Badge 
                  dot={selectedUser.is_online} 
                  status={selectedUser.is_online ? 'success' : 'default'} 
                />
              </Space>
            ) : (
              'Chọn người dùng để bắt đầu trò chuyện'
            )
          }
          style={{ height: '100%' }}
          styles={{ 
            body: { 
              padding: 0, 
              height: 'calc(100% - 57px)', 
              display: 'flex', 
              flexDirection: 'column' 
            }
          }}
        >
          {selectedUser ? (
            <>
              {/* Messages Area */}
              <div className="chat-messages">
                {messages.length === 0 ? (
                  <Empty 
                    description="Chưa có tin nhắn nào"
                    image={Empty.PRESENTED_IMAGE_SIMPLE}
                  />
                ) : (
                  <List
                    dataSource={Array.isArray(messages) ? messages : []}
                    renderItem={(msg) => (
                      <List.Item style={{ border: 'none', padding: '8px 0' }}>
                        <div className={`message-bubble ${msg.is_own_message ? 'own' : 'other'}`}>
                          <div className={`message-content ${msg.is_own_message ? 'own' : 'other'}`}>
                            <div>{msg.content}</div>
                            <div className="message-time">
                              {dayjs(msg.timestamp).format('HH:mm')}
                            </div>
                          </div>
                        </div>
                      </List.Item>
                    )}
                  />
                )}
              </div>

              {/* Message Input */}
              <div className="message-input-area">
                <Space.Compact style={{ width: '100%' }}>
                  <TextArea
                    value={messageText}
                    onChange={(e) => setMessageText(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Nhập tin nhắn..."
                    autoSize={{ minRows: 1, maxRows: 4 }}
                    style={{ flex: 1 }}
                  />
                  <Button
                    type="primary"
                    icon={<SendOutlined />}
                    onClick={sendMessage}
                    loading={sending}
                    disabled={!messageText.trim()}
                  >
                    Gửi
                  </Button>
                </Space.Compact>
              </div>
            </>
          ) : (
            <div className="empty-chat">
              <MessageOutlined style={{ fontSize: 64, color: '#d9d9d9', marginBottom: 16 }} />
              <Text type="secondary">Chọn một người dùng để bắt đầu trò chuyện</Text>
            </div>
          )}
        </Card>
      </Col>
    </Row>
  )
}
