<template>
  <div class="hello">
    <h1>{{ msg }}</h1>
     <!-- <img src="./assets/logo.png"> -->
     <img class="logo" :src="avatar" height="150" width="150"/>
    <el-row>
    <el-input
      placeholder="Please enter the search content"
      v-model="input"
      @keyup.enter.native="search"
      clearable>
    </el-input>
    <el-button  class="butt"
                type="primary" 
                icon="el-icon-search"
                @click="search">Search</el-button>
    </el-row>
    <el-row>
    <p>Sort by: </p>
    <el-radio-group v-model="radio">
    <!-- <el-radio :label="1">test</el-radio> -->
    <el-radio :label="2">BM25</el-radio>
    <el-radio :label="3">TF-IDF</el-radio>
    <el-radio :label="4">TF-simi</el-radio>
    <el-radio :label="5">Jaccard</el-radio>
    <el-radio :label="6">BetterTf-IDF</el-radio>
    </el-radio-group>
    </el-row>
  </div>
</template>

<script>
import api from '../axios'
import avatar from '@/assets/search.png'
export default {
  name: 'HelloWorld',
  data () {
    return {
      avatar: avatar,
      msg: 'Welcome to Wing',
      input: '',
      radio:  2
    }
  },
  methods: {
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
      }
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h1, h2 {
  font-weight: normal;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
.butt {
  margin-top:10px;
}
</style>
