import { useState, useEffect } from 'react'
import {
  Card,
  Row,
  Col,
  Button,
  Typography,
  Modal,
  Select,
  message,
  Spin,
  Statistic,
  Progress,
  Space,
  List,
  Badge
} from 'antd'
import {
  BugOutlined,
  TrophyOutlined,
  ThunderboltOutlined,
  PlusOutlined,
  DeleteOutlined,
  GiftOutlined
} from '@ant-design/icons'
import { farmAPI } from '../../services/api'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import '../../styles/Farm.css'

// Add relativeTime plugin for dayjs
dayjs.extend(relativeTime)

// Interfaces
interface CropType {
  id: number
  name: string
  emoji: string
  seed_price: number
  sell_price: number
  growth_time_minutes: number
}

interface Plot {
  plot_number: number
  state: 'empty' | 'planted' | 'ready' | 'withered'
  crop_type?: CropType
  time_until_ready?: number
}

interface Farm {
  level: number
  energy: number
  max_energy: number
  experience: number
  experience_to_next_level?: number
  plots_unlocked: number
  plots?: Plot[]
}

interface FarmStats {
  total_crops_planted: number
  total_crops_harvested: number
  total_money_earned: number
  total_money_spent: number
}

interface Transaction {
  id: number
  transaction_type: string
  amount: number
  description: string
  created_at: string
}

const { Title, Text } = Typography
const { Option } = Select

export default function FarmPage() {
  const [loading, setLoading] = useState(true)
  const [farm, setFarm] = useState<Farm | null>(null)
  const [crops, setCrops] = useState<CropType[]>([])
  const [stats, setStats] = useState<FarmStats>({} as FarmStats)
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [plantModalVisible, setPlantModalVisible] = useState(false)
  const [selectedPlot, setSelectedPlot] = useState<number | null>(null)
  const [selectedCrop, setSelectedCrop] = useState<number | null>(null)

  useEffect(() => {
    loadFarmData()
  }, [])

  const loadFarmData = async () => {
    try {
      setLoading(true)
      
      const [farmRes, cropsRes] = await Promise.all([
        farmAPI.getFarm().catch(() => ({ data: null })),
        farmAPI.getCrops().catch(() => ({ data: [] }))
      ])

      // Try to load stats and transactions
      let farmStats: FarmStats = {
        total_crops_planted: 0,
        total_crops_harvested: 0,
        total_money_earned: 0,
        total_money_spent: 0
      }
      let farmTransactions: Transaction[] = []

      try {
        const statsRes = await farmAPI.getStats()
        farmStats = statsRes.data
      } catch (error) {
        console.log('Farm stats not available')
      }

      try {
        const transactionsRes = await farmAPI.getTransactions()
        farmTransactions = Array.isArray(transactionsRes.data) ? transactionsRes.data.slice(0, 10) : []
      } catch (error) {
        console.log('Farm transactions not available')
      }

      setFarm(farmRes.data)
      setCrops(Array.isArray(cropsRes.data) ? cropsRes.data : [])
      setStats(farmStats)
      setTransactions(farmTransactions)
    } catch (error) {
      console.error('Error loading farm data:', error)
      message.error('Không thể tải dữ liệu trang trại')
    } finally {
      setLoading(false)
    }
  }

  const plantCrop = async () => {
    if (!selectedPlot || !selectedCrop) return

    try {
      await farmAPI.plantCrop(selectedPlot, selectedCrop)
      message.success('Trồng cây thành công!')
      setPlantModalVisible(false)
      setSelectedPlot(null)
      setSelectedCrop(null)
      loadFarmData()
    } catch (error) {
      console.error('Error planting crop:', error)
      message.error('Không thể trồng cây')
    }
  }

  const harvestPlot = async (plotNumber: number) => {
    try {
      const response = await farmAPI.harvestPlot(plotNumber)
      message.success(response.data.message)
      loadFarmData()
    } catch (error) {
      console.error('Error harvesting plot:', error)
      message.error('Không thể thu hoạch')
    }
  }

  const clearPlot = async (plotNumber: number) => {
    try {
      await farmAPI.clearPlot(plotNumber)
      message.success('Dọn dẹp ô đất thành công!')
      loadFarmData()
    } catch (error) {
      console.error('Error clearing plot:', error)
      message.error('Không thể dọn dẹp ô đất')
    }
  }

  const harvestAll = async () => {
    try {
      const response = await farmAPI.harvestAll()
      message.success(response.data.message)
      loadFarmData()
    } catch (error) {
      console.error('Error harvesting all:', error)
      message.error('Không thể thu hoạch tất cả')
    }
  }

  const openPlantModal = (plotNumber: number) => {
    setSelectedPlot(plotNumber)
    setPlantModalVisible(true)
  }

  const renderPlot = (plot: Plot) => {
    const getPlotClass = () => {
      switch (plot.state) {
        case 'empty': return 'empty'
        case 'planted': return 'planted'
        case 'ready': return 'ready'
        case 'withered': return 'withered'
        default: return 'empty'
      }
    }

    const getPlotContent = () => {
      switch (plot.state) {
        case 'empty':
          return (
            <div onClick={() => openPlantModal(plot.plot_number)}>
              <PlusOutlined style={{ fontSize: 20, color: '#8b4513' }} />
              <div style={{ fontSize: 10 }}>Trống</div>
            </div>
          )
        case 'planted':
          return (
            <div>
              <div style={{ fontSize: 20 }}>{plot.crop_type?.emoji || '🌱'}</div>
              <div style={{ fontSize: 8 }}>Đang trồng</div>
              {plot.time_until_ready && (
                <div style={{ fontSize: 8 }}>
                  {Math.floor(plot.time_until_ready / 60)}p
                </div>
              )}
            </div>
          )
        case 'ready':
          return (
            <div onClick={() => harvestPlot(plot.plot_number)}>
              <div style={{ fontSize: 20 }}>{plot.crop_type?.emoji || '🌾'}</div>
              <div style={{ fontSize: 8 }}>Sẵn sàng</div>
            </div>
          )
        case 'withered':
          return (
            <div onClick={() => clearPlot(plot.plot_number)}>
              <DeleteOutlined style={{ fontSize: 20, color: '#ff4d4f' }} />
              <div style={{ fontSize: 8 }}>Héo</div>
            </div>
          )
        default:
          return null
      }
    }

    return (
      <div
        key={plot.plot_number}
        className={`farm-plot ${getPlotClass()}`}
        style={{ cursor: 'pointer' }}
      >
        {getPlotContent()}
      </div>
    )
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

  if (!farm) {
    return (
      <Card>
        <div style={{ textAlign: 'center', padding: 40 }}>
          <BugOutlined style={{ fontSize: 64, color: '#d9d9d9' }} />
          <Title level={3}>Chưa có trang trại</Title>
          <Text type="secondary">Trang trại sẽ được tạo tự động khi bạn bắt đầu chơi</Text>
        </div>
      </Card>
    )
  }

  const energyPercentage = (farm.energy / farm.max_energy) * 100
  const experienceToNext = farm.experience_to_next_level || 0
  
  // Calculate grid columns based on plots unlocked
  const gridCols = Math.ceil(Math.sqrt(farm.plots_unlocked))

  return (
    <div>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Title level={2}>🌱 Trang trại của tôi</Title>
        <Button 
          type="primary" 
          icon={<GiftOutlined />}
          onClick={harvestAll}
        >
          Thu hoạch tất cả
        </Button>
      </div>

      {/* Farm Status */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="Cấp độ"
              value={farm.level}
              prefix={<TrophyOutlined />}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <div>
              <Text type="secondary">Năng lượng</Text>
              <div style={{ display: 'flex', alignItems: 'center', marginTop: 4 }}>
                <ThunderboltOutlined style={{ color: '#faad14', marginRight: 8 }} />
                <Progress 
                  percent={energyPercentage} 
                  showInfo={false} 
                  strokeColor="#faad14"
                  style={{ flex: 1 }}
                />
                <Text style={{ marginLeft: 8, fontSize: 12 }}>
                  {farm.energy}/{farm.max_energy}
                </Text>
              </div>
            </div>
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="Kinh nghiệm"
              value={farm.experience}
              suffix={experienceToNext > 0 ? `/${experienceToNext + farm.experience}` : ''}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="Ô đất mở"
              value={farm.plots_unlocked}
              suffix="/20"
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        {/* Farm Grid */}
        <Col xs={24} lg={16}>
          <Card title="Trang trại">
            <div 
              className="farm-grid"
              style={{ 
                gridTemplateColumns: `repeat(${gridCols}, 1fr)`,
                gridTemplateRows: `repeat(${Math.ceil(farm.plots_unlocked / gridCols)}, 1fr)`
              }}
            >
              {farm.plots?.map(plot => renderPlot(plot))}
            </div>
          </Card>
        </Col>

        {/* Farm Info */}
        <Col xs={24} lg={8}>
          <Space direction="vertical" style={{ width: '100%' }}>
            {/* Farm Stats */}
            <Card title="Thống kê trang trại" size="small">
              <Row gutter={16}>
                <Col span={12}>
                  <Statistic
                    title="Cây đã trồng"
                    value={stats.total_crops_planted || 0}
                    valueStyle={{ fontSize: 16 }}
                  />
                </Col>
                <Col span={12}>
                  <Statistic
                    title="Đã thu hoạch"
                    value={stats.total_crops_harvested || 0}
                    valueStyle={{ fontSize: 16 }}
                  />
                </Col>
                <Col span={12}>
                  <Statistic
                    title="Tiền kiếm được"
                    value={stats.total_money_earned || 0}
                    suffix="đ"
                    valueStyle={{ fontSize: 16 }}
                  />
                </Col>
                <Col span={12}>
                  <Statistic
                    title="Đã chi tiêu"
                    value={stats.total_money_spent || 0}
                    suffix="đ"
                    valueStyle={{ fontSize: 16 }}
                  />
                </Col>
              </Row>
            </Card>

            {/* Available Crops */}
            <Card title="Cây trồng có sẵn" size="small">
              <List
                dataSource={Array.isArray(crops) ? crops.slice(0, 5) : []}
                renderItem={(crop) => (
                  <List.Item>
                    <List.Item.Meta
                      avatar={<span style={{ fontSize: 20 }}>{crop.emoji}</span>}
                      title={crop.name}
                      description={
                        <Space direction="vertical" size={0}>
                          <Text type="secondary">
                            💰 {crop.seed_price}đ → {crop.sell_price}đ
                          </Text>
                          <Text type="secondary">
                            ⏱️ {crop.growth_time_minutes}p
                          </Text>
                        </Space>
                      }
                    />
                  </List.Item>
                )}
                size="small"
              />
            </Card>

            {/* Recent Transactions */}
            <Card title="Giao dịch gần đây" size="small">
              <List
                dataSource={Array.isArray(transactions) ? transactions : []}
                renderItem={(transaction) => (
                  <List.Item>
                    <List.Item.Meta
                      avatar={
                        <Badge 
                          dot 
                          status={transaction.amount > 0 ? 'success' : 'error'}
                        />
                      }
                      title={
                        <Space>
                          <Text style={{ fontSize: 12 }}>
                            {transaction.transaction_type === 'seed_purchase' ? 'Mua hạt giống' :
                             transaction.transaction_type === 'crop_harvest' ? 'Thu hoạch' :
                             transaction.description}
                          </Text>
                          <Text 
                            style={{ 
                              fontSize: 12,
                              color: transaction.amount > 0 ? '#52c41a' : '#ff4d4f'
                            }}
                          >
                            {transaction.amount > 0 ? '+' : ''}{transaction.amount}đ
                          </Text>
                        </Space>
                      }
                      description={
                        <Text type="secondary" style={{ fontSize: 10 }}>
                          {dayjs(transaction.created_at).fromNow()}
                        </Text>
                      }
                    />
                  </List.Item>
                )}
                size="small"
              />
            </Card>
          </Space>
        </Col>
      </Row>

      {/* Plant Crop Modal */}
      <Modal
        title="Chọn cây trồng"
        open={plantModalVisible}
        onCancel={() => {
          setPlantModalVisible(false)
          setSelectedPlot(null)
          setSelectedCrop(null)
        }}
        onOk={plantCrop}
        okText="Trồng"
        cancelText="Hủy"
        okButtonProps={{ disabled: !selectedCrop }}
      >
        <div style={{ marginBottom: 16 }}>
          <Text>Ô đất số: <strong>{selectedPlot}</strong></Text>
        </div>
        
        <Select
          style={{ width: '100%' }}
          placeholder="Chọn loại cây trồng"
          value={selectedCrop}
          onChange={setSelectedCrop}
        >
          {Array.isArray(crops) ? crops.map(crop => (
            <Option key={crop.id} value={crop.id}>
              <Space>
                <span>{crop.emoji}</span>
                <span>{crop.name}</span>
                <Text type="secondary">
                  ({crop.seed_price}đ - {crop.growth_time_minutes}p)
                </Text>
              </Space>
            </Option>
          )) : []}
        </Select>
      </Modal>
    </div>
  )
}
