import AdminApiMixin from '@/admin/mixins/admin-api'
import CommonMixin from '@/admin/mixins/common-mixin'
import store from '@/store/index'
import Message from '@/admin/utils/message'
// import mockup from '@/admin/mockup/orderList.json'

export default {
  store: store,
  mixins: [AdminApiMixin, CommonMixin],
  data() {
    return {
      list: [],
      page: 1,
      total: 0,
      pageLen: 50,
      loading: false,
      filter: {},
      detailData: {},
      detailHistory: [],
      sellerAttribute: []
    }
  },
  created() {
    // this.getMeta()
  },
  computed: {
    prefixUrl() {
      return this.constants.apiDomain
    },
    maxPage() {
      return Math.ceil(this.total / this.pageLen)
    },
    constants() {
      return this.$store.state.const
    },
    // 주문 리스트
    listUrl() {
      return this.prefixUrl + '/orders'
    },
    // 주문 상세 / 수정
    detailUrl() {
      return this.prefixUrl + '/orders'
    },
    // 셀러 리스트 / 수정
    metaUrl() {
      return this.prefixUrl + '/orders/ready/init'
    },
    // 배송처리
    deliveryUrl() {
      return this.prefixUrl + '/orders'
    },
    offset() {
      return (this.page - 1) * this.pageLen
    },
    checkedList() {
      const newList = []
      this.list.forEach(d => { if (d.checked) newList.push(d) })
      return newList
    }
  },
  methods: {
    load() {
      this.loading = true
      const params = JSON.parse(JSON.stringify(this.filter))
      params.limit = this.pageLen
      params.offset = this.offset
      params.order_status_type_id = 1 // 상품 준비 상태
      // {{domain}}/orders?order_status_type_id=1&start_date=2021-04-30&end_date=2021-04-01&sub_property_id=1

      // new Promise((resolve, reject) => {
      //   setTimeout(() => {
      //     this.$emit('test', { a: 1 })
      //     resolve(listMockup())
      //   }, 300)
      // })
      this.get(this.listUrl, {
        params: params
      })
        .then((res) => {
          const orderList = res.data.result.order_list
          orderList.forEach((d) => {
            d.checked = false
          })
          this.total = res.data.result.total_count
          this.list = orderList
        }).catch((e) => {
          if (e.code === 'ECONNABORTED') {
            Message.error('요청 시간을 초과 하였습니다. 다시 시도해주시기 바랍니다.')
          } else {
            console.log(e)
            Message.error('처리 중 오류 발생')
          }
        }).then((res) => {
          this.loading = false
        })
    },
    getDetail(orderNo) {
      this.loading = true
      this.get(this.detailUrl + '/' + orderNo)
        .then((res) => {
          if (res.data) {
            this.detailData = res.data.result.order_detail
            this.detailHistory = res.data.result.order_history
          } else {
            Message.error('통신 실패')
          }
        }).catch((e) => {
          if (e.code === 'ECONNABORTED') {
            Message.error('요청 시간을 초과 하였습니다. 다시 시도해주시기 바랍니다.')
          } else {
            Message.error('처리 중 오류 발생')
          }
        }).then((res) => {
          this.loading = false
        })
    },
    changePage(page) {
      this.page = page
      this.load()
    },
    setFilter(filter) {
      this.filter = filter
    },
    getMeta() {
      this.get(this.metaUrl)
        .then((res) => {
          if (res.data) {
            this.sellerAttribute = res.data.result.data.sellerAttribute
          } else {
            Message.error('통신 실패')
          }
        }).catch((e) => {
          if (e.code === 'ECONNABORTED') {
            Message.error('요청 시간을 초과 하였습니다. 다시 시도해주시기 바랍니다.')
          } else {
            Message.error('처리 중 오류 발생')
          }
        }).then((res) => {
          // this.loading = false
        })
    },
    async setDelivery(list) {
      if (list.length > 0) {
        try {
          const payload = []
          list.forEach(order => {
            payload.push({ orders_detail_id: order.orders_detail_id, order_status_type_id: 3 })
          })
          const res = await this.patch(this.deliveryUrl, payload)
          const failCount = res.data.post_fail.length
          const successCount = list.length - failCount

          if (failCount === 0) {
            Message.success('배송처리가 완료되었습니다.')
            this.load()
            return
          }
          // 일부 성공, 일부 실패
          if (failCount > 0 && successCount > 0) {
            Message.warning(`${failCount}건의 배송처리가 실패하고 ${successCount}이 배송되었습니다.`)
            this.load()
            return
          }

          // 일부 성공, 일부 실패
          if (failCount > 0 && successCount === 0) {
            Message.error(`${failCount}건의 배송처리가 모두 실패 하여습니다.`)
            return
          }
        } catch (e) {
          Message.error(e.response.data.user_error_message)
        }
      }
      // 배송처리
      // /master/order/ready/<order_id>
      // {
      //    "message": "updated",
      //    "result": "PATCH"
      // }
    }
  },
  watch: {
    pageLen(v) {
      this.changePage(1)
    }
  }
}
