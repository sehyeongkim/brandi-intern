<template>
  <div>
    <h2>상품 관리</h2>
    <product-filter-box @search="search"/>
    <div class="divide">
      <a-select style="width: 100px; float:right; " v-model="dataStore.pageLen">
        <a-select-option :value="item.value" v-for="item in rowCounts" :key="item.value">{{ item.label }}</a-select-option>
      </a-select>
      <div style="float:left; line-height: 32px;">상품관리 / 상품 관리 > 상품관리 관리 > 리스트</div>
      <div style="clear:both"></div>
    </div>
    <div class="table-header-buttons">
      <a-button size="small" type="success">선택한 상품 엑셀다운로드</a-button>
      <a-button size="small" type="success">전체상품 엑셀다운로드</a-button>

      <a-select style="width: 120px" v-model="batchUpdate.selling">
        <a-select-option value="">판매여부</a-select-option>
        <a-select-option value="1">판매</a-select-option>
        <a-select-option value="0">미판매</a-select-option>
      </a-select>
      <a-select style="width: 120px" v-model="batchUpdate.display">
        <a-select-option value="">진열여부</a-select-option>
        <a-select-option value="1">진열</a-select-option>
        <a-select-option value="0">미진열</a-select-option>
      </a-select>
      <a-button
        type="warning"
        :disabled="batchUpdate.selling === '' && batchUpdate.display === ''"
        @click="doBatchUpdate"
      >적용</a-button>
    </div>

    <board-list :data-store="dataStore" :height="500" @change-page="changePage">
      <template slot="header">
        <th>등록일</th>
        <th>대표이미지</th>
        <th>상품명</th>
        <th>상품코드</th>
        <th>상품번호</th>
        <th>셀러속성</th>
        <th>셀러명</th>
        <th>판매가</th>
        <th>할인가</th>
        <th>판매여부</th>
        <th>진열여부</th>
        <th>할인여부</th>
        <th>Actions</th>
      </template>
      <template slot="row" slot-scope="{item}">
        <!--
discount_price: 12000
discount_rate: 0.2
id: 4
image_url: "https://cdn.pixabay.com/photo/2015/04/23/22/00/tree-736885__340.jpg"
is_displayed: 1
is_selling: 1
korean_brand_name: "라라"
price: 15000
product_code: "444"
seller_id: 4
sub_property: "디자이너브랜드"
title: "믓진 아우터 "
upload_date: "2021-04-20 "
          -->
        <td>{{ item.upload_date }}</td> <!-- 등록일 -->
        <td><img :src="item.image_url" width="70" height="70"></td> <!-- 대표이미지 -->
        <td>{{ item.title }}</td> <!-- 상품명 -->
        <td><router-link :to="'products/'+item.product_code">{{ item.product_code }}</router-link></td> <!-- 상품코드 -->
        <td>{{ item.id }}</td> <!-- 상품번호 -->
        <td>{{ item.sub_property }}</td> <!-- 셀러속성 -->
        <td>{{ item.korean_brand_name }}</td> <!-- 셀러명 -->
        <td>{{ item.price | makeComma }}</td> <!-- 판매가 -->
        <td>{{ item.discount_price | makeComma }} <span class="discount-rate" v-if="item.discount_rate > 0">({{ item.discount_rate * 100 }}%)</span></td> <!-- 할인가 -->
        <td>{{ item.is_selling | typeToName('saleTypes') }}</td> <!-- 판매여부 -->
        <td>{{ item.is_displayed | typeToName('exhibitTypes') }}</td> <!-- 진열여부 -->
        <td><!--{{ getProductDiscountTypeName(item.is_discount) }}-->
          {{ item.discount_rate > 0 ? 1: 0 | typeToName('discountTypes') }}
        </td> <!-- 할인여부 -->
        <td>
          <a-button type="primary" size="small" @click="buyProduct(item)">구매하기</a-button>
        </td>
      </template>
    </board-list>
    <order-modal
       ref="orderModal"
    />
  </div>
</template>

<script>
import Vue from 'vue'
import store from '../product-store'
import ProductFilterBox from './product-filter-box'
import BoardList from '@/admin/Components/Common/BoardList'
import CommonMixin from '@/admin/mixins/common-mixin'
import Message from '@/admin/utils/message'
import errors from '@/admin/errors/errors'
import OrderModal from './order-modal'
const ExpireTokenException = errors.ExpireTokenException
const TimeoutException = errors.TimeoutException

export default {
  name: 'product-list',
  mixins: [CommonMixin],
  components: { BoardList, ProductFilterBox, OrderModal },
  data() {
    return {
      dataStore: new Vue(store),
      batchUpdate: {
        selling: '',
        display: ''
      },
      rowCounts: [
        { label: '10개', value: 10 },
        { label: '20개', value: 20 },
        { label: '50개', value: 50 }
      ]
    }
  },
  mounted() {
    this.dataStore.$on('test', (d) => {
      console.log('aa', d)
    })
  },
  methods: {
    doBatchUpdate() {
      // 상품 상태 일괄 변경
      const checkedList = this.dataStore.getCheckedList()
      if (checkedList.length === 0) {
        Message.error('체크된 상품이 없습니다.')
        return
      }
      if (confirm(`${checkedList.length}건의 상품을 일괄 변경 하시겠습니까?`)) {
        this.dataStore.batchUpdate(checkedList, this.batchUpdate)
      }
    },
    search(filter) {
      this.dataStore.page = 1
      this.dataStore.setFilter(filter)
      this.load()
    },
    // 상품 구매
    buyProduct(row) {
      console.log('상품 구매', row)
      this.$refs.orderModal.show(row)
    },
    changePage(page) {
      console.log('page', page)
      this.dataStore.changePage(page)
      this.load()
    },
    load() {
      this.dataStore.load()
        .then((res) => {})
        .catch((e) => {
          // 토큰 만료 처리
          if (e instanceof ExpireTokenException) {
            Message.error(e.message, () => {
              this.$router.push('/')
            })
          } else if (e instanceof TimeoutException) {
            Message.error(e.message)
          } else {
            Message.error(e.message)
          }
        })
    }
  },
  computed: {
  }
}
</script>
<style scoped>
.divide {
  background: #F1F1F1;
  padding: 5px 10px;
  margin-left: -20px;
  margin-right: -20px;
  font-size: 12px;
  font-weight: bold;
}
.table-header-buttons {
  text-align: right;
  margin: 5px;
}
.discount-rate {
  color: red;
}

</style>
