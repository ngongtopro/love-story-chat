import { useState, useEffect } from 'react'
import {
  Card,
  Row,
  Col,
  Button,
  Typography,
  List,
  Modal,
  Form,
  InputNumber,
  Input,
  message,
  Spin,
  Statistic,
  Badge,
  Space,
  Tabs
} from 'antd'
import {
  WalletOutlined,
  PlusOutlined,
  MinusOutlined,
  DollarOutlined,
  HistoryOutlined,
  TrophyOutlined
} from '@ant-design/icons'
import { walletAPI } from '../../services/api'
import dayjs from 'dayjs'

const { Title, Text } = Typography
const { TabPane } = Tabs

interface Wallet {
  balance: number
}

interface Transaction {
  id: number
  transaction_type: string
  amount: number
  description?: string
  created_at: string
  balance_after?: number
}

interface WalletStats {
  total_transactions?: number
  total_earned?: number
}

interface AddBalanceValues {
  amount: number
  description: string
}

interface DeductBalanceValues {
  amount: number
  description: string
}

export default function WalletPage() {
  const [loading, setLoading] = useState(true)
  const [wallet, setWallet] = useState<Wallet | null>(null)
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [stats, setStats] = useState<WalletStats>({})
  const [addModalVisible, setAddModalVisible] = useState(false)
  const [deductModalVisible, setDeductModalVisible] = useState(false)
  const [processing, setProcessing] = useState(false)

  useEffect(() => {
    loadWalletData()
  }, [])

  const loadWalletData = async () => {
    try {
      setLoading(true)
      
      const [walletRes, transactionsRes] = await Promise.all([
        walletAPI.getWallet().catch(() => ({ data: null })),
        walletAPI.getTransactions().catch(() => ({ data: [] }))
      ])

      // Try to load stats
      let walletStats: WalletStats = {}
      try {
        const statsRes = await walletAPI.getStats()
        walletStats = statsRes.data
      } catch (error) {
        console.log('Wallet stats not available')
      }

      setWallet(walletRes.data)
      setTransactions(Array.isArray(transactionsRes.data) ? transactionsRes.data : [])
      setStats(walletStats)
    } catch (error) {
      console.error('Error loading wallet data:', error)
      message.error('Không thể tải dữ liệu ví')
    } finally {
      setLoading(false)
    }
  }

  const addBalance = async (values: AddBalanceValues) => {
    try {
      setProcessing(true)
      await walletAPI.addBalance(values.amount, values.description)
      message.success('Nạp tiền thành công!')
      setAddModalVisible(false)
      loadWalletData()
    } catch (error) {
      console.error('Error adding balance:', error)
      message.error('Không thể nạp tiền')
    } finally {
      setProcessing(false)
    }
  }

  const deductBalance = async (values: DeductBalanceValues) => {
    try {
      setProcessing(true)
      await walletAPI.deductBalance(values.amount, values.description)
      message.success('Rút tiền thành công!')
      setDeductModalVisible(false)
      loadWalletData()
    } catch (error) {
      console.error('Error deducting balance:', error)
      message.error('Không thể rút tiền')
    } finally {
      setProcessing(false)
    }
  }

  const getTransactionIcon = (transaction: Transaction) => {
    switch (transaction.transaction_type) {
      case 'game_win':
        return <TrophyOutlined style={{ color: '#52c41a' }} />
      case 'game_bet':
        return <DollarOutlined style={{ color: '#ff4d4f' }} />
      case 'admin_add':
        return <PlusOutlined style={{ color: '#1890ff' }} />
      case 'admin_deduct':
        return <MinusOutlined style={{ color: '#ff4d4f' }} />
      default:
        return <HistoryOutlined />
    }
  }

  const getTransactionType = (transaction: Transaction) => {
    switch (transaction.transaction_type) {
      case 'game_win': return 'Thắng game'
      case 'game_bet': return 'Cược game'
      case 'admin_add': return 'Nạp tiền'
      case 'admin_deduct': return 'Rút tiền'
      case 'initial': return 'Số dư ban đầu'
      default: return transaction.transaction_type
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

  if (!wallet) {
    return (
      <Card>
        <div style={{ textAlign: 'center', padding: 40 }}>
          <WalletOutlined style={{ fontSize: 64, color: '#d9d9d9' }} />
          <Title level={3}>Chưa có ví</Title>
          <Text type="secondary">Ví sẽ được tạo tự động khi bạn bắt đầu sử dụng</Text>
        </div>
      </Card>
    )
  }

  return (
    <div>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Title level={2}>💰 Ví của tôi</Title>
        <Space>
          <Button 
            type="primary" 
            icon={<PlusOutlined />}
            onClick={() => setAddModalVisible(true)}
          >
            Nạp tiền
          </Button>
          <Button 
            icon={<MinusOutlined />}
            onClick={() => setDeductModalVisible(true)}
          >
            Rút tiền
          </Button>
        </Space>
      </div>

      {/* Wallet Balance */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="Số dư hiện tại"
              value={wallet.balance}
              precision={0}
              suffix="đ"
              prefix={<WalletOutlined />}
              valueStyle={{ color: '#3f8600', fontSize: 24 }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={8}>
          <Card>
            <Statistic
              title="Tổng giao dịch"
              value={stats.total_transactions || 0}
              prefix={<HistoryOutlined />}
            />
          </Card>
        </Col>
        <Col xs={12} sm={8}>
          <Card>
            <Statistic
              title="Tổng thu nhập"
              value={stats.total_earned || 0}
              suffix="đ"
              prefix={<TrophyOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Transactions */}
      <Card>
        <Tabs defaultActiveKey="all">
          <TabPane tab="Tất cả giao dịch" key="all">
            <List
              dataSource={transactions}
              renderItem={(transaction) => (
                <List.Item>
                  <List.Item.Meta
                    avatar={getTransactionIcon(transaction)}
                    title={
                      <Space>
                        <Text>{getTransactionType(transaction)}</Text>
                        <Badge 
                          count={
                            <Text style={{
                              color: transaction.amount > 0 ? '#52c41a' : '#ff4d4f',
                              fontSize: 14,
                              fontWeight: 'bold'
                            }}>
                              {transaction.amount > 0 ? '+' : ''}{transaction.amount?.toLocaleString()}đ
                            </Text>
                          }
                          showZero
                          style={{ backgroundColor: 'transparent' }}
                        />
                      </Space>
                    }
                    description={
                      <Space direction="vertical" size={0}>
                        {transaction.description && (
                          <Text type="secondary">{transaction.description}</Text>
                        )}
                        <Space>
                          <Text type="secondary" style={{ fontSize: 12 }}>
                            {dayjs(transaction.created_at).format('DD/MM/YYYY HH:mm')}
                          </Text>
                          <Text type="secondary" style={{ fontSize: 12 }}>
                            Số dư: {transaction.balance_after?.toLocaleString()}đ
                          </Text>
                        </Space>
                      </Space>
                    }
                  />
                </List.Item>
              )}
              locale={{ emptyText: 'Chưa có giao dịch nào' }}
            />
          </TabPane>
          
          <TabPane tab="Thu nhập" key="income">
            <List
              dataSource={transactions.filter(t => t.amount > 0)}
              renderItem={(transaction) => (
                <List.Item>
                  <List.Item.Meta
                    avatar={getTransactionIcon(transaction)}
                    title={
                      <Space>
                        <Text>{getTransactionType(transaction)}</Text>
                        <Text style={{ color: '#52c41a', fontWeight: 'bold' }}>
                          +{transaction.amount?.toLocaleString()}đ
                        </Text>
                      </Space>
                    }
                    description={
                      <Space direction="vertical" size={0}>
                        {transaction.description && (
                          <Text type="secondary">{transaction.description}</Text>
                        )}
                        <Text type="secondary" style={{ fontSize: 12 }}>
                          {dayjs(transaction.created_at).format('DD/MM/YYYY HH:mm')}
                        </Text>
                      </Space>
                    }
                  />
                </List.Item>
              )}
              locale={{ emptyText: 'Chưa có giao dịch thu nhập' }}
            />
          </TabPane>
          
          <TabPane tab="Chi tiêu" key="expense">
            <List
              dataSource={transactions.filter(t => t.amount < 0)}
              renderItem={(transaction) => (
                <List.Item>
                  <List.Item.Meta
                    avatar={getTransactionIcon(transaction)}
                    title={
                      <Space>
                        <Text>{getTransactionType(transaction)}</Text>
                        <Text style={{ color: '#ff4d4f', fontWeight: 'bold' }}>
                          {transaction.amount?.toLocaleString()}đ
                        </Text>
                      </Space>
                    }
                    description={
                      <Space direction="vertical" size={0}>
                        {transaction.description && (
                          <Text type="secondary">{transaction.description}</Text>
                        )}
                        <Text type="secondary" style={{ fontSize: 12 }}>
                          {dayjs(transaction.created_at).format('DD/MM/YYYY HH:mm')}
                        </Text>
                      </Space>
                    }
                  />
                </List.Item>
              )}
              locale={{ emptyText: 'Chưa có giao dịch chi tiêu' }}
            />
          </TabPane>
        </Tabs>
      </Card>

      {/* Add Balance Modal */}
      <Modal
        title="Nạp tiền vào ví"
        open={addModalVisible}
        onCancel={() => setAddModalVisible(false)}
        footer={null}
      >
        <Form
          layout="vertical"
          onFinish={addBalance}
        >
          <Form.Item
            name="amount"
            label="Số tiền (đồng)"
            rules={[
              { required: true, message: 'Vui lòng nhập số tiền!' },
              { type: 'number', min: 1000, message: 'Số tiền tối thiểu là 1,000đ' }
            ]}
          >
            <InputNumber
              style={{ width: '100%' }}
              formatter={value => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
              parser={value => value ? value.replace(/\$\s?|(,*)/g, '') : ''}
              placeholder="Nhập số tiền"
            />
          </Form.Item>

          <Form.Item
            name="description"
            label="Ghi chú"
            initialValue="Nạp tiền vào ví"
          >
            <Input placeholder="Ghi chú cho giao dịch" />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button onClick={() => setAddModalVisible(false)}>
                Hủy
              </Button>
              <Button type="primary" htmlType="submit" loading={processing}>
                Nạp tiền
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* Deduct Balance Modal */}
      <Modal
        title="Rút tiền từ ví"
        open={deductModalVisible}
        onCancel={() => setDeductModalVisible(false)}
        footer={null}
      >
        <Form
          layout="vertical"
          onFinish={deductBalance}
        >
          <Form.Item
            name="amount"
            label="Số tiền (đồng)"
            rules={[
              { required: true, message: 'Vui lòng nhập số tiền!' },
              { type: 'number', min: 1000, message: 'Số tiền tối thiểu là 1,000đ' },
              { type: 'number', max: wallet.balance, message: 'Số dư không đủ!' }
            ]}
          >
            <InputNumber
              style={{ width: '100%' }}
              formatter={value => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
              parser={value => value ? value.replace(/\$\s?|(,*)/g, '') : ''}
              placeholder="Nhập số tiền"
            />
          </Form.Item>

          <Form.Item
            name="description"
            label="Ghi chú"
            initialValue="Rút tiền từ ví"
          >
            <Input placeholder="Ghi chú cho giao dịch" />
          </Form.Item>

          <div style={{ marginBottom: 16 }}>
            <Text type="secondary">
              Số dư hiện tại: <strong>{wallet.balance?.toLocaleString()}đ</strong>
            </Text>
          </div>

          <Form.Item>
            <Space>
              <Button onClick={() => setDeductModalVisible(false)}>
                Hủy
              </Button>
              <Button type="primary" htmlType="submit" loading={processing}>
                Rút tiền
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
