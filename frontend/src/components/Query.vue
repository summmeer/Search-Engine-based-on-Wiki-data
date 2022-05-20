<template>
  <el-container class="container">
      <div class="main">
      <el-header>
      <el-row :gutter="20">
        <el-col :span="17">
            <div class="input">
            <el-input
        placeholder="Please enter the search content"
        v-model="input"
        @keyup.enter.native="search"
        clearable>
        </el-input>
        </div>
        </el-col>
        <el-col :span="2">
            <div class="search">
                <el-button type="primary" 
                            icon="el-icon-search"
                            @click="search">Search</el-button>
            </div>
        </el-col>
    </el-row>
    <div class="radio">
    <el-radio-group v-model="radio">
    <!-- <el-radio :label="1">test</el-radio> -->
    <el-radio :label="2">BM25</el-radio>
    <el-radio :label="3">TF-IDF</el-radio>
    <el-radio :label="4">TF-simi</el-radio>
    <el-radio :label="5">Jaccard</el-radio>
    <el-radio :label="6">BetterTf-IDF</el-radio>
    </el-radio-group>
    </div>
      </el-header>
    <p v-if="searchTime" align="left" class="time">Total search time {{searchTime}} ms</p>
    <div class="results">
      <div v-for="item in pageContent" v-bind:key="item.id" class="item">
        <a @click="goToArticle(item.id)" class="hlink">{{ item.title }}</a>
        <br>
        <p align="left" class="text" v-html="item.window"></p>      
      </div>
    </div>
      </div>
    <el-footer class="footer">
    <div class="block">
        <br>
    <el-pagination
      v-if="total"
      @current-change="handleCurrentChange"
      :current-page.sync="curPage"
      :page-size="page_size"
      layout="total,prev, pager, next, jumper"
      :total="total">
    </el-pagination>
  </div>
      </el-footer>
  </el-container>
</template>


<script>
import api from '../axios'

export default {
  name: 'HelloWorld',
  data () {
    return {
      msg: 'Welcome to Our Search Engine',
      input: "",
      radio: 2,
      page_size: 6,
      pageContent: null,
    //   idsLen: null,
      curPage: 0,
      total: null,
      searchTime: null,
    }
  },
  mounted () {
      console.log(this.$route.params)
      console.log(this.$route.query.p)
      this.input = this.$route.params.q
      this.radio = parseInt(this.$route.params.t)
      this.curPage = parseInt(this.$route.query.p)
    //   this.handleCurrentChange(parseInt(this.$route.query.p))
      let data = {
        query: this.input,
        type: this.radio,
        page_size: this.page_size,
        page: this.curPage
      }
      let that = this
      api.search(data).then((res) => {
          console.log(res.data)
          that.pageContent = res.data['firstPage']
          that.total = res.data['idsLen']
          that.searchTime = res.data['time']
      }, (err) => {
      })
  },
  methods: {
      goToArticle(id) {
          let url = '/article/'+id+"/"
            this.$router.push({ path: url })
      },
      handleCurrentChange(val) {
        console.log(`当前页: ${val}`);
        console.log(this.curPage)
        let url = "/search/" + this.input + "/" + this.radio + "?p=" + val
    //     let start = (this.curPage-1)*this.page_size
    //     let end = this.curPage*this.page_size
    //     console.log(start)
    //     console.log(end)
    //     let data = {
    //         ids: this.ids.slice(start, end),
    //         query: this.input
    //     }
    //     let that = this
    //     api.getPage(data).then((res) => {
    //       console.log(res.data)
    //       that.pageContent = res.data
    //   }, (err) => {
    //   })
        let data = {
            query: this.input,
            type: this.radio,
            page_size: this.page_size,
            page: val
        }
        let that = this
        api.search(data).then((res) => {
            console.log(res.data)
            that.pageContent = res.data['firstPage']
        }, (err) => {
        })
        this.$router.push({ path: url })
      },
      search() {
          if(this.input=='') {
            this.$message({
            showClose: true,
            message: 'Please enter the search content',
            type: 'error'
            });
        } else {
            let url = '/search/'+this.input+"/"+this.radio + "?p=1"
            this.$router.push({ path: url })
            location.reload()
        }
      }
  }
}
</script>

<style scoped>
.input {
  margin-left: 40px;
}

.search {
  margin-left: 0px;
}

.radio {
  float: left;
  margin-left: 40px;
  margin-top: 10px;
}

.block {
    float: left;
    margin-left: 40px;
    margin-top: 10px;
}

.item {
    float: left;
    margin-left: 50px;
    margin-top: 11px;
    width: 900px
}

.text {
    /* float: left;
    margin-top: 0px;
    margin-left: 0px; */
    margin-top: 5px;
    text-align: left;
    /* position:absolute;
    left: 60px; */
}
.text >>> span{
        color:crimson;
}

.hlink {
    float: left;
    margin-bottom: 1px;
    color:blue;
    text-decoration:underline;
}
.results {
    float: left;
    margin-left: 20px;
    align: left;
}

.red {
    color:crimson;
}
.footer{
    height:35px;
    position:absolute;
    bottom:5px;
}
.container{
    min-height:100%;
    position:absolute;
}
.main{
    padding-bottom: 40px;
}
.time{
    margin-left: 60px;
    margin-top:25px;
    size: 5;
    color:black;
}
</style>