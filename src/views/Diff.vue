<template>
  <div>
    <div class="search">
      <a-input
        placeholder="输入左边 URL"
        v-model.trim="leftUrl"
        allowClear
      ></a-input>
      <a-input
        placeholder="输入右边 URL"
        v-model.trim="rightUrl"
        allowClear
        style="margin-top: 5px"
      />
      <a-button type="primary" @click="diffUrl" style="margin: 5px"
        >对比</a-button
      >
    </div>
    <div class="content">
      <a-spin :spinning="spinning">
        <code-diff
          v-if="leftStr != '' || rightStr != ''"
          :old-string="leftStr"
          :new-string="rightStr"
          outputFormat="side-by-side"
          renderNothingWhenEmpty
          isShowNoChange
          :context="500"
        />
      </a-spin>
    </div>
  </div>
</template>
<script>
import { Input, Spin, Button } from "ant-design-vue";
import { CodeDiff } from "v-code-diff";

export default {
  name: "home",
  data() {
    return {
      spinning: false,
      leftUrl: "",
      rightUrl: "",
      leftStr: "左边 URL 内容",
      rightStr: "右边 URL 内容",
      mode: "split",
      theme: "light",
      language: "plaintext"
    };
  },
  components: {
    AInput: Input,
    ASpin: Spin,
    AButton: Button,
    CodeDiff
  },
  methods: {
    diffUrl() {
      if (
        typeof this.leftUrl === "undefined" ||
        this.leftUrl === null ||
        this.leftUrl === ""
      ) {
        this.$message.warning("请输入左边 URL!");
        return;
      }
      if (
        typeof this.rightUrl === "undefined" ||
        this.rightUrl === null ||
        this.rightUrl === ""
      ) {
        this.$message.warning("请输入右边 URL!");
        return;
      }
      this.leftStr = "";
      this.rightStr = "";
      this.getData();
    },
    getData() {
      let that = this;
      that.spinning = true;
      that.$axios
        .get(this.leftUrl)
        .then(function(response) {
          that.leftStr = response.data;
        })
        .catch(function(error) {
          // handle error
          console.log(error);
        })
        .then(function() {
          // always executed
          that.spinning = false;
        });
      that.spinning = true;
      that.$axios
        .get(this.rightUrl)
        .then(function(response) {
          // handle success
          that.rightStr = response.data;
        })
        .catch(function(error) {
          // handle error
          that.rightStr = error;
          console.log(error);
        })
        .then(function() {
          // always executed
          that.spinning = false;
        });
    }
  },
  mounted() {
    // this.diffUrl();
  },
  computed: {}
};
</script>

<style scoped>
@min-width: 1000px;

.search {
  @media screen {
    @media (min-width: @min-width) {
      width: 600px;
    }
    @media (max-width: @min-width) {
      font-size: 12px;
      padding: 50px 10px 20px;
    }
  }
  margin: 0 auto;
  text-align: center;
  padding: 50px 10px;
}

.content {
  width: 100%;
  /* padding: 0px 80px 20px 80px; */
  /* @media screen {
    @media (max-width: @min-width) {
      padding: 0 20px 20px 20px;
    }
  } */
}
</style>
