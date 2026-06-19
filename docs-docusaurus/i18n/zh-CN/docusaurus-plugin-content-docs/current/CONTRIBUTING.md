# 为 Kalico 做出贡献

感谢您为 Kalico 做出贡献！本文档描述了向 Kalico 贡献更改的过程。

有关报告问题或联系开发者的详细信息，请参见 [contact 页面](Contact.md)。

## 贡献流程概述

对 Kalico 的贡献通常遵循以下高级流程：

1. 提交者首先创建 [GitHub Pull Request](https://github.com/KalicoCrew/kalico/pulls)，当提交准备好进行大规模部署时。
2. 当 [reviewer](#reviewers) 可以 [review](#what-to-expect-in-a-review) 该提交时，他们将在 GitHub 上将自己分配给该 Pull Request。review 的目标是查找缺陷并检查提交是否遵循文档中指定的指南。
3. 成功 review 后，reviewer 将在 GitHub 上"approve the review"，然后 [maintainer](#reviewers) 将将更改提交到 Kalico `main` 分支。

在进行功能增强时，考虑在 [Kalico Discord 服务器](Contact.md#discord) 上开始（或参与）一个讨论串。
论坛上的持续讨论可以提高开发工作的可见性，并可能吸引其他对测试新工作感兴趣的人。

## review 中的期望

对 Kalico 的贡献在合并之前会进行 review。review 过程的主要目标是检查缺陷并检查提交是否遵循 Kalico 文档中指定的指南。

我们知道完成一项任务有很多方法；review 的目的不是讨论"最佳"实现。在可能的情况下，基于事实和测量的 review 讨论是更可取的。

大多数提交都会收到 review 反馈。请准备好获取反馈、提供进一步详细信息，并在需要时更新提交。

reviewer 会查看的常见问题：

1. 提交是否没有缺陷并且准备好进行大规模部署？

   提交者应在提交前测试其更改。reviewer 会查找错误，但通常不会测试提交。被接受的提交通常在接受后的几周内部署到数千台打印机。因此，提交的质量被认为是优先考虑的。

   主要的 [KalicoCrew/kalico](https://github.com/KalicoCrew/kalico) GitHub 仓库可能接受实验性工作，但我们鼓励提交者在自己的仓库中进行实验、调试和测试。[Kalico Discord 服务器](Contact.md#discord) 是提高新工作知名度和寻找有兴趣提供实际反馈的用户的好地方。

   提交必须通过所有 [回归测试用例](Debugging.md)。

   在修复代码中的缺陷时，提交者应大致了解该缺陷的根本原因，修复应针对该根本原因。

   代码提交不应包含过多的调试代码、调试选项或运行时调试日志。

   代码提交中的注释应侧重于增强代码维护。提交不应包含"注释掉的代码"或过多描述过去实现的注释。不应有过多的"todo"注释。

   文档更新不应声明它们是"正在进行中"。

2. 提交是否为执行实际任务的实际用户提供了"高影响"益处？

   reviewer 需要至少在他们自己心中确定大致"目标受众是谁"、"该受众的规模"、他们将获得的"益处"、"如何衡量该益处"以及"这些测量测试的结果"。在大多数情况下，这对提交者和 reviewer 都是显而易见的，在 review 期间不会明确说明。

   提交到 Kalico `main` 分支的提交应具有值得注意的目标受众。作为一般"经验法则"，提交应针对至少 100 名实际用户的基础。

   如果 reviewer 要求提供关于提交"益处"的详细信息，请不要认为这是批评。能够理解更改的实际好处是 review 的自然组成部分。

   在讨论益处时，最好讨论"事实和测量"。通常，reviewer 不会寻找"有人可能发现选项 X 有用"这种形式的回应，也不会寻找"此提交添加了固件 X 实现的功能"这种形式的回应。相反，通常更倾向于讨论如何衡量质量改进以及这些测量的结果的详细信息 - 例如，"在 Acme X1000 打印机上的测试显示改善的角部，如图片所示……"，或者例如"在 Foomatic X900 打印机上实际对象 X 的打印时间从 4 小时缩短到 3.5 小时"。我们知道这种类型的测试可能需要大量时间和精力。Kalico 的一些最著名功能在合并到 `main` 分支之前经过了数月的讨论、返工、测试和文档编写。

   所有新模块、配置选项、命令、命令参数和文档都应具有"高影响"。我们不想给用户带来他们无法合理配置的选项负担，也不想给他们带来没有明显益处的选项负担。

   reviewer 可能会要求澄清用户如何配置选项 - 理想的回应将包含有关该过程的详细信息 - 例如，"MegaX500 的用户应将选项 X 设置为 99.3，而 Elite100Y 的用户应使用程序……校准选项 X"。

   如果选项的目标是使代码更模块化，则最好使用代码常量而不是面向用户的配置选项。

   新模块、新选项和新参数不应提供与现有模块类似的功能 - 如果差异是任意的，则最好使用现有系统或重构现有代码。

3. 提交的版权是否清晰、非无偿且兼容？

   新的 C 文件和 Python 文件应有明确的版权声明。有关首选格式，请参见现有文件。对现有文件进行小改动时宣布版权是不鼓励的。

   从第三方来源获取的代码必须与 Kalico 许可证（GNU GPLv3）兼容。大型第三方代码添加应添加到 `lib/` 目录（并遵循 [lib/README](../lib/README) 中描述的格式）。

   提交者必须使用其真实全名提供 [Signed-off-by 行](#format-of-commit-messages)。它表明提交者同意 [developer certificate of origin](developer-certificate-of-origin)。

4. 提交是否遵循 Kalico 文档中指定的指南？

   特别是，代码应遵循 [Code_Overview.md](Code_Overview.md) 中的指南，配置文件应遵循 [Example_Configs.md](Example_Configs.md) 中的指南。

5. Kalico 文档是否已更新以反映新更改？

   至少，参考文档必须更新以对应代码中的更改：
   * 所有命令和命令参数必须在 [G-Codes.md](G-Codes.md) 中记录。
   * 所有面向用户的模块及其配置参数必须在 [Config_Reference.md](Config_Reference.md) 中记录。
   * 所有导出的"status variables"必须在 [Status_Reference.md](Status_Reference.md) 中记录。
   * 所有新的"webhooks"及其参数必须在 [API_Server.md](API_Server.md) 中记录。
   * 任何对命令或配置文件设置进行非向后兼容更改的更改都必须在 [Config_Changes.md](Config_Changes.md) 中记录。

   新文档应添加到 [Overview.md](Overview.md) 并添加到网站索引 [docs/_kalico/mkdocs.yml](../docs/_kalico/mkdocs.yml)。

6. 提交信息是否格式良好、每个提交解决单个主题且相互独立？

   提交信息应遵循 [首选格式](#format-of-commit-messages)。

   提交不得有合并冲突。Kalico `main` 分支的新添加始终通过"rebase"或"squash and rebase"完成。通常不需要提交者在每次更新 Kalico `main` 分支时重新合并其提交。但是，如果有合并冲突，建议提交者使用 `git rebase` 来解决冲突。

   每个提交应解决单个高级更改。大型更改应拆分为多个独立的提交。每个提交应"独立存在"，以便 `git bisect` 和 `git revert` 等工具可靠工作。

   空白更改不应与功能更改混合在一起。通常，除非来自被修改代码的既定"所有者"，否则不会接受无意义的空白更改。

Kalico 在 Python 代码上实现了软严格的"编码风格指南"。对现有代码的修改应遵循现有代码的高级代码流程、代码缩进风格和格式。

review 的目的不是讨论"更好的实现"。但是，如果 reviewer 难以理解提交的实现，则可能会要求更改以使实现更加透明。特别是，如果 reviewer 无法说服自己提交没有缺陷，则可能需要进行更改。

作为 review 的一部分，reviewer 可能会为某个主题创建一个替代 Pull Request。这可能是为了避免在次要程序性事项上过多的"来回讨论"，从而简化提交过程。也可能是因为讨论启发 reviewer 构建替代实现。这两种情况都是 review 的正常结果，不应被视为对原始提交的批评。

### 协助 review

我们感谢协助 review！不需要是 [列出的 reviewer](#reviewers) 才能执行 review。也鼓励 GitHub Pull Request 的提交者审查自己的提交。

要协助 review，请按照 [review 中的期望](#what-to-expect-in-a-review) 中概述的步骤验证提交。完成 review 后，将您的发现作为评论添加到 GitHub Pull Request。如果提交通过了 review，请在评论中明确说明 - 例如类似"我根据 CONTRIBUTING 文档中的步骤审查了此更改，一切看起来都很好"的内容。如果无法完成 review 中的某些步骤，请明确说明哪些步骤已审查以及哪些步骤未审查 - 例如类似"我没有检查代码中的缺陷，但我审查了 CONTRIBUTING 文档中的其他所有内容，看起来很好"的内容。

我们还感谢对提交的测试。如果测试了代码，请将您的测试结果（成功或失败）作为评论添加到 GitHub Pull Request。请明确说明代码已测试以及结果 - 例如类似"我在我的 Acme900Z 打印机上测试了此代码并进行了花瓶打印，结果很好"的内容。

### Reviewer

Kalico 的"reviewer"有：

| 姓名                   | GitHub Id         | 感兴趣领域 |
| ---------------------- | ----------------- | ---------- |

*TODO*

请不要"ping"任何 reviewer，也不要直接将提交指向他们。所有 reviewer 都会监控论坛和 PR，并在有时间时进行 review。

Kalico 的"maintainer"有：

| 姓名                   | GitHub name       |
| ---------------------- | ----------------- |
| Bea Nance              | @bwnance          |
| Rogerio Goncalves      | @rogerlz          |
| Lasse Dalegaard        | @dalegaard        |

## 提交信息格式

每个提交的提交信息应类似于以下格式：

```
module: Capitalized, short (50 chars or less) summary

More detailed explanatory text, if necessary.  Wrap it to about 75
characters or so.  In some contexts, the first line is treated as the
subject of an email and the rest of the text as the body.  The blank
line separating the summary from the body is critical (unless you omit
the body entirely); tools like rebase can get confused if you run the
two together.

Further paragraphs come after blank lines..

Signed-off-by: My Name <myemail@example.org>
```

在上面的示例中，`module` 应该是仓库中文件或目录的名称（不带文件扩展名）。例如，`clocksync: Fix typo in pause() call at connect time`。在提交信息中指定模块名称的目的是帮助为提交评论提供上下文。

在每个提交上都有"Signed-off-by"行很重要 - 它证明您同意 [developer certificate of origin](developer-certificate-of-origin)。它必须包含您的真实姓名（抱歉，不接受化名或匿名贡献）和当前电子邮件地址。
