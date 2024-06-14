<template>
  <div>
    <div class="search">
      <a-input-search
        placeholder="输入 Kind or Group"
        v-model.trim="search_text"
        @search="onSearch"
        allowClear
        enterButton="搜索..."
      />
    </div>
    <div class="content">
      <a-spin :spinning="spinning">
        <div v-if="searchData.length == 0">
          <div class="tools">
            <a-dropdown>
              <a-menu
                slot="overlay"
                @click="handleMenuClick"
                style="height: 500px;overflow: auto;"
              >
                <a-menu-item :key="item" v-for="item in version_list">
                  <a-icon type="search" />{{ item }}
                </a-menu-item>
              </a-menu>
              <a-button style="margin-left: 8px">
                当前版本: <span v-text="version" style="margin-left:5px"></span>
                <a-icon type="down" />
              </a-button>
            </a-dropdown>
            <a-button type="text" @click="showModal" style="margin-left: 5px"
              >对比 API</a-button
            >
            <router-link
              tag="button"
              class="ant-btn ant-btn-text"
              style="margin-left: 5px"
              id="diff"
              to="/diff"
              >对比 URL 文件</router-link
            >
          </div>
          <a-table :columns="columns" :data-source="data">
            <span slot="versions" slot-scope="versions, url">
              <a-tag v-for="v in versions" :key="v" color="green">
                <a
                  target="_blank"
                  :href="
                    url['url'] +
                      '/#' +
                      url['kind'].toLowerCase() +
                      '-' +
                      v +
                      '-' +
                      url['group'].replace(/\./g, '-').toLowerCase()
                  "
                  >{{ v }}</a
                >
              </a-tag>
            </span>
          </a-table>
        </div>
        <div v-else>
          <a-table
            :columns="searchColumns"
            :data-source="searchData"
            @change="handleSearchChange"
          >
            <span slot="k8s" slot-scope="k8s, url">
              <a target="_blank" :href="url['url']">{{ k8s }}</a>
            </span>
            <span slot="versions" slot-scope="versions, url">
              <a-tag v-for="v in versions" :key="v" color="green">
                <a
                  target="_blank"
                  :href="
                    url['url'] +
                      '/#' +
                      url['kind'].toLowerCase() +
                      '-' +
                      v +
                      '-' +
                      url['group'].replace(/\./g, '-').toLowerCase()
                  "
                  >{{ v }}</a
                >
              </a-tag>
            </span>
          </a-table>
        </div>
      </a-spin>
    </div>

    <a-modal
      v-model="visible"
      title="版本 API 对比"
      @ok="handleOk"
      @cancel="handleCancel"
      :maskClosable="false"
      width="1480px"
    >
      <div style="padding-bottom: 5px">
        左边版本：
        <a-select style="width: 120px" @change="handleLeftChange">
          <a-select-option v-for="version in version_list" :key="version">
            {{ version }}
          </a-select-option>
        </a-select>
        右边版本：
        <a-select style="width: 120px" @change="handleRightChange">
          <a-select-option v-for="version in version_list" :key="version">
            {{ version }}
          </a-select-option>
        </a-select>
      </div>
      <div>
        <code-diff
          :old-string="leftStr"
          :new-string="rightStr"
          outputFormat="side-by-side"
          renderNothingWhenEmpty
          isShowNoChange
          :context="500"
        />
      </div>
    </a-modal>
  </div>
</template>

<script>
import {
  Input,
  Spin,
  Table,
  Dropdown,
  Menu,
  Icon,
  Tag,
  Button,
  Modal,
  Select
} from "ant-design-vue";
import { CodeDiff } from "v-code-diff";

export default {
  name: "home",
  data() {
    return {
      spinning: true,
      kindFilter: [],
      groupFilter: [],
      versionFilter: [],
      data: [],
      api_data: {},
      version: "",
      version_list: [],
      search_text: "",
      searchData: [],
      sortedInfo: null,
      api_html:
        "https://kubernetes.io/docs/reference/generated/kubernetes-api/",
      visible: false,
      rightStr: "右边版本内容",
      leftStr: "左边版本内容",
      mode: "split",
      theme: "light",
      language: "plaintext"
    };
  },
  components: {
    AInputSearch: Input.Search,
    ASpin: Spin,
    ATable: Table,
    ADropdown: Dropdown,
    AMenu: Menu,
    AMenuItem: Menu.Item,
    AIcon: Icon,
    ATag: Tag,
    AButton: Button,
    AModal: Modal,
    ASelect: Select,
    ASelectOption: Select.Option,
    CodeDiff
  },
  methods: {
    onSearch(value) {
      if (typeof value === "undefined" || value === null || value === "") {
        this._getData();
        this.searchData = [];
      } else {
        this.getSearchData(value);
      }
    },
    handleMenuClick(e) {
      this.spinning = true;
      this.version = e.key;
      this.getVersionData();
      this.spinning = false;
    },
    handleSearchChange(pagination, filters, sorter) {
      this.sortedInfo = sorter;
    },
    getVersionData() {
      this.data = [];
      this.kindFilter = [];
      this.groupFilter = [];
      let n = 1;
      let kind_list = [];
      let group_list = [];
      for (var key in this.api_data[this.version]) {
        if (kind_list.indexOf(key) === -1) {
          kind_list.push(key);
          this.kindFilter.push({
            text: key,
            value: key
          });
        }
        for (var gkey in this.api_data[this.version][key]) {
          this.data.push({
            key: n,
            url:
              this.api_html +
              this.version
                .split(".")
                .slice(0, 2)
                .join("."),
            kind: key,
            group: gkey,
            version: this.api_data[this.version][key][gkey]
          });
          n += 1;
          if (group_list.indexOf(gkey) === -1) {
            group_list.push(gkey);
            this.groupFilter.push({
              text: gkey,
              value: gkey
            });
          }
        }
      }
      this.kindFilter.sort(function(a, b) {
        return a["text"].localeCompare(b["text"]);
      });
      this.groupFilter.sort(function(a, b) {
        return a["text"].localeCompare(b["text"]);
      });
    },
    getSearchData(search = "") {
      this.searchData = [];
      let n = 1;
      for (var k8s_key in this.api_data) {
        for (var kind_key in this.api_data[k8s_key]) {
          let is_kind = false;
          if (kind_key.toLowerCase().indexOf(search.toLowerCase()) !== -1) {
            is_kind = true;
          }
          for (var group_key in this.api_data[k8s_key][kind_key]) {
            if (
              is_kind ||
              group_key.toLowerCase().indexOf(search.toLowerCase()) !== -1
            ) {
              this.searchData.push({
                key: n,
                k8s: k8s_key,
                url:
                  this.api_html +
                  k8s_key
                    .split(".")
                    .slice(0, 2)
                    .join("."),
                kind: kind_key,
                group: group_key,
                version: this.api_data[k8s_key][kind_key][group_key]
              });
              n += 1;
            }
          }
        }
      }
      if (this.searchData.length === 0) {
        this.$message.warning("未查到信息，请换个关键字！");
      } else {
        this.sortedInfo = {
          order: "ascend",
          columnKey: "k8s"
        };
      }
    },
    _getData() {
      this.spinning = true;
      this.$axios
        .get("static/data/data.json")
        .then(rep => {
          this.api_data = rep.data;
          for (var key in this.api_data) {
            this.version_list.push(key);
          }

          this.version_list.sort(function(a, b) {
            return a.replace("v", "") > b.replace("v", "") ? -1 : 1;
          });
          for (var v_key in this.version_list) {
            this.versionFilter.push({
              text: this.version_list[v_key],
              value: this.version_list[v_key]
            });
          }
          this.version = this.version_list[0];
          this.getVersionData();
          this.spinning = false;
        })
        .catch(e => {
          this.$message.error("获取数据失败!");
          console.log(e);
        });
    },
    showModal() {
      this.visible = true;
      this.rightStr = "右边版本内容";
      this.leftStr = "左边版本内容";
    },
    handleOk(e) {
      console.log(e);
      this.visible = false;
    },
    handleCancel(e) {
      console.log(e);
      this.visible = false;
    },
    handleLeftChange(value) {
      let str = [];
      for (var key in this.api_data[value]) {
        for (var gkey in this.api_data[value][key]) {
          str.push(
            key +
              " " +
              gkey +
              " " +
              this.api_data[value][key][gkey].sort().join(",")
          );
        }
      }
      this.leftStr = str.sort().join("\n");
    },
    handleRightChange(value) {
      console.log(value);
      let str = [];
      for (var key in this.api_data[value]) {
        for (var gkey in this.api_data[value][key]) {
          str.push(
            key +
              " " +
              gkey +
              " " +
              this.api_data[value][key][gkey].sort().join(",")
          );
        }
      }
      this.rightStr = str.sort().join("\n");
    }
  },
  mounted() {
    this._getData();
  },
  computed: {
    columns() {
      const columns = [
        {
          title: "Kind",
          dataIndex: "kind",
          filters: this.kindFilter,
          onFilter: (value, record) => record.kind === value,
          sorter: (a, b) => a.kind.localeCompare(b.kind)
        },
        {
          title: "Group",
          dataIndex: "group",
          filters: this.groupFilter,
          onFilter: (value, record) => record.group === value,
          sorter: (a, b) => a.group.localeCompare(b.group)
        },
        {
          title: "Version",
          dataIndex: "version",
          scopedSlots: { customRender: "versions" }
        }
      ];
      return columns;
    },
    searchColumns() {
      const searchColumns = [
        {
          title: "K8s Version",
          dataIndex: "k8s",
          filters: this.versionFilter,
          sortOrder:
            this.sortedInfo.columnKey === "k8s" && this.sortedInfo.order,
          onFilter: (value, record) => record.k8s === value,
          sorter: (a, b) =>
            a.k8s.replace("v", "") > b.k8s.replace("v", "") ? -1 : 1,
          scopedSlots: { customRender: "k8s" }
        },
        {
          title: "Kind",
          dataIndex: "kind",
          filters: this.kindFilter,
          onFilter: (value, record) => record.kind === value,
          sorter: (a, b) => a.kind.localeCompare(b.kind)
        },
        {
          title: "Group",
          dataIndex: "group",
          filters: this.groupFilter,
          onFilter: (value, record) => record.group === value,
          sorter: (a, b) => a.group.localeCompare(b.group)
        },
        {
          title: "Version",
          dataIndex: "version",
          scopedSlots: { customRender: "versions" }
        }
      ];
      return searchColumns;
    }
  }
};
</script>

<style lang="less" scoped>
@min-width: 1000px;

.list-title {
  font-size: 16px;
  font-weight: bolder;
  font-family: "微软雅黑";
}

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
  padding: 0px 80px 20px 80px;
  @media screen {
    @media (max-width: @min-width) {
      padding: 0 20px 20px 20px;
    }
  }
}
.ant-list-item-meta-description {
  @media screen {
    @media (max-width: @min-width) {
      font-size: 12px;
    }
  }
  .tag-title {
    @media screen {
      @media (max-width: @min-width) {
        display: none;
      }
    }
  }
  .ant-tag {
    @media screen {
      @media (max-width: @min-width) {
        margin: 0;
      }
    }
  }
}
.tips {
  margin-top: 10px;
  font-size: 14px;
}
.tips-tag {
  @media screen {
    @media (max-width: @min-width) {
      font-size: 12px;
    }
  }
  margin-bottom: 5px;
}

.header-switch {
  float: right;
}

.list-header {
  @media screen {
    @media (max-width: @min-width) {
      font-size: 12px;
    }
  }
}

.tools {
  margin-bottom: 20px;
}
</style>
